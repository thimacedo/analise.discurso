import json
import httpx
import asyncio
import time
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from core.config import settings
from core.forensics_service import forensics_service

# --- SENTINELA | Diamond Intelligence Engine v42.1 ---
# IntegraÃ§Ã£o MCF v2.0: Cascata Resiliente e CCF Framework.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinela-ai")

class AIEngine(ABC):
    """Classe base para motores de IA do Sentinela."""

    @abstractmethod
    async def classify(self, text: str) -> Optional[Dict[str, Any]]:
        pass

class GeminiEngine(AIEngine):
    async def classify(self, text: str) -> Optional[Dict[str, Any]]:
        if not settings.GEMINI_API_KEY: return None
        # Usando v1beta para suporte a response_mime_type: application/json
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
        system_prompt = forensics_service.get_system_prompt()
        payload = {
            "contents": [{"parts": [{"text": f"{system_prompt}\n\nTEXTO: \"{text}\""}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    raw_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    return forensics_service.parse_verdict(raw_text)
            except Exception as e:
                logger.warning(f"âš ï¸ [AI] Gemini failure: {e}")
        return None

class GroqEngine(AIEngine):
    async def classify(self, text: str) -> Optional[Dict[str, Any]]:
        if not settings.GROQ_API_KEY: return None
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
        system_prompt = forensics_service.get_system_prompt()
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"TEXTO: \"{text}\""}
            ],
            "response_format": {"type": "json_object"}
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=headers, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    raw_text = resp.json()['choices'][0]['message']['content']
                    return forensics_service.parse_verdict(raw_text)
            except Exception as e:
                logger.warning(f"âš ï¸ [AI] Groq failure: {e}")
        return None

class OllamaEngine(AIEngine):
    async def classify(self, text: str) -> Optional[Dict[str, Any]]:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        system_prompt = forensics_service.get_system_prompt()
        payload = {
            "model": "gemma:2b",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"TEXTO: \"{text}\""}
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1}
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=30.0)
                if resp.status_code == 200:
                    raw_text = resp.json().get("message", {}).get("content", "")
                    return forensics_service.parse_verdict(raw_text)
            except Exception as e:
                logger.warning(f"âš ï¸ [AI] Ollama failure: {e}")
        return None

class AIService:
    def __init__(self, db_client=None):
        self.db = db_client
        self.engines: Dict[str, AIEngine] = {}
        self.engine_scores: Dict[str, int] = {
            "gemini": 100,
            "groq": 90,
            "ollama": 80
        }
        self.engine_latencies: Dict[str, float] = {}

        # Auto-registro padrÃ£o
        self.register_engine("gemini", GeminiEngine())
        self.register_engine("groq", GroqEngine())
        self.register_engine("ollama", OllamaEngine())

    def register_engine(self, name: str, engine: AIEngine):
        """Registra um novo motor de IA."""
        self.engines[name] = engine
        if name not in self.engine_scores:
            self.engine_scores[name] = 50
        logger.debug(f"[AI] Motor registrado: {name}")

    def _get_cascade_order(self) -> List[str]:
        """Retorna a ordem dos motores baseada em pontuaÃ§Ã£o."""
        return sorted(self.engines.keys(), key=lambda k: self.engine_scores.get(k, 0), reverse=True)

    async def classify(self, text: str) -> Dict[str, Any]:
        """Classifica texto usando cascata de motores com sistema de recompensa e penalidade de latÃªncia."""
        if not text or not text.strip():
            return {"categoria_ia": "NEUTRO", "confianca_ia": 1.0, "is_hate": False, "reason": "Input vazio", "engine": "none"}

        start_time = time.perf_counter()
        cascade_order = self._get_cascade_order()

        for engine_name in cascade_order:
            engine = self.engines.get(engine_name)
            if not engine: continue

            result = await engine.classify(text)
            if result:
                latency = time.perf_counter() - start_time

                # Registro de auditoria PASA
                forensics_service.log_audit(text, result, engine_name, latency)

                if self.engine_scores[engine_name] >= 100:
                    last_latency = self.engine_latencies.get(engine_name, float('inf'))
                    if latency >= last_latency:
                        self.engine_scores[engine_name] -= 5
                    else:
                        logger.info(f"âš¡ [AI] {engine_name.upper()} bateu recorde de velocidade ({latency:.2f}s).")
                else:
                    self.engine_scores[engine_name] = min(100, self.engine_scores[engine_name] + 2)

                self.engine_latencies[engine_name] = latency
                result["latency"] = latency
                result["engine"] = engine_name
                logger.info(f"ðŸ“Š [AI] {engine_name.upper()} | {result.get('categoria_ia')} | {result['latency']:.2f}s")
                return result
            else:
                self.engine_scores[engine_name] = max(0, self.engine_scores[engine_name] - 15)

        return {
            "categoria_ia": "NEUTRO",
            "confianca_ia": 0.0,
            "is_hate": False,
            "reason": "Cascata de IA esgotada",
            "engine": "fail",
            "latency": time.perf_counter() - start_time
        }

    async def run_batch_classification(self, limit: int = 200, force_retry_failures: bool = False):
        """Processamento em lote com persistÃªncia via DB injetado."""
        from core.db import db_client
        from core.pasa_auditor import PASAAuditor
        self.db = db_client
        pasa_auditor = PASAAuditor(ai_service_instance=self)

        total_processed = 0

        if force_retry_failures:
            logger.info("ðŸ” [AI] Iniciando limpeza de FALHA_IA...")
            res = self.db.client.table('comentarios').select('*').eq('categoria_ia', 'FALHA_IA').limit(limit).execute()
            comentarios = res.data
        else:
            comentarios = await self.db.fetch_unprocessed_comments(limit=limit)

        if comentarios:
            logger.info(f"ðŸ§  [AI] Processando lote de {len(comentarios)} comentÃ¡rios...")
            updates = []
            for c in comentarios:
                result_full = await pasa_auditor.process(c.get('texto_bruto', ''))
                res = result_full.get("classification", {})
                engine = res.get("engine", "none")
                
                updates.append({
                    "id": c['id'],
                    "is_hate": res.get('is_hate', False),
                    "categoria_ia": res.get('categoria_ia', 'NEUTRO'),
                    "direcao_odio": res.get('direcao_odio'),
                    "ccf_density": res.get('ccf_density', 0.0),
                    "ccf_sync": res.get('ccf_sync', 0.0),
                    "ccf_performativity": res.get('ccf_performativity', 0.0),
                    "confianca_ia": res.get('confianca_ia', 0.0),
                    "processado_ia": True if engine != 'fail' else False
                })

            if updates:
                await self.db.batch_update_comments(updates)
                logger.info(f"ðŸ’¾ [AI] Persistidos {len(updates)} comentÃ¡rios com CCF Framework.")
                total_processed += len(updates)

        return total_processed

# Singleton
ai_service = AIService()
