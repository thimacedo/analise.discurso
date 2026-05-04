import json
import httpx
import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from core.config import settings

# --- SENTINELA | Diamond Intelligence Engine v16.4 ---
# Refatoração Implacável: Cascata Resiliente e Latência Zero.

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinela-ai")

SYSTEM_PROMPT_PASA = """
Você é um analista forense do sistema Sentinela Democrática. Classifique o texto segundo o Protocolo PASA v16.4.

CATEGORIAS EXATAS:
- NEUTRO (Críticas, protestos, debates ideológicos NÃO são ódio).
- ODIO_IDENTITARIO (Xenofobia, racismo, regionalismo).
- VIOLENCIA_GENERO (Misoginia, ofensas à condição feminina).
- AMEACA (Incitação a dano físico ou morte).
- INSULTO_AD_HOMINEM (Desumanização: lixo, rato, verme, escória).
- ATAQUE_INSTITUCIONAL (Deslegitimação de órgãos como STF/TSE).
- RIGOR_CRIMINAL (Imputação de crime sem prova: ladrão, corrupto).

SAÍDA: JSON VÁLIDO.
{"category": "CATEGORIA", "confidence": 0.95, "is_hate": true, "reason": "motivo"}
"""

class AIEngine(ABC):
    """Classe base para motores de IA do Sentinela."""
    
    @abstractmethod
    async def classify(self, text: str) -> Optional[Dict[str, Any]]:
        pass

    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parser resiliente para respostas de IA (Diamond Pattern)."""
        try:
            # Limpeza de markdown e ruídos
            clean = text.strip()
            if clean.startswith("```"):
                clean = clean.split("\n", 1)[-1]
            if clean.endswith("```"):
                clean = clean.rsplit("\n", 1)[0]
            clean = clean.replace('```json', '').replace('```', '').strip()
            
            data = json.loads(clean)
            cat = str(data.get("category", "NEUTRO")).upper().replace("ODEIO", "ODIO").strip()
            
            valid_categories = [
                "NEUTRO", "ODIO_IDENTITARIO", "VIOLENCIA_GENERO", 
                "AMEACA", "INSULTO_AD_HOMINEM", "ATAQUE_INSTITUCIONAL", "RIGOR_CRIMINAL"
            ]
            if cat not in valid_categories: 
                cat = "NEUTRO"
            
            return {
                "category": cat,
                "confidence": float(data.get("confidence", 0.0)),
                "is_hate": bool(data.get("is_hate", False)),
                "reason": data.get("reason", "Análise automatizada v16.4")
            }
        except Exception as e:
            logger.debug(f"[AI Parse] Erro ao decodificar JSON: {e} | Raw: {text[:100]}...")
            return {"category": "NEUTRO", "confidence": 0.0, "is_hate": False, "reason": "Erro de parser PASA"}

class GeminiEngine(AIEngine):
    async def classify(self, text: str) -> Optional[Dict[str, Any]]:
        if not settings.GEMINI_API_KEY: return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT_PASA}\n\nTEXTO: \"{text}\""}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    raw_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    return self._parse_response(raw_text)
            except Exception as e:
                logger.warning(f"⚠️ [AI] Gemini failure: {e}")
        return None

class GroqEngine(AIEngine):
    async def classify(self, text: str) -> Optional[Dict[str, Any]]:
        if not settings.GROQ_API_KEY: return None
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_PASA},
                {"role": "user", "content": f"TEXTO: \"{text}\""}
            ],
            "response_format": {"type": "json_object"}
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=headers, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    raw_text = resp.json()['choices'][0]['message']['content']
                    return self._parse_response(raw_text)
            except Exception as e:
                logger.warning(f"⚠️ [AI] Groq failure: {e}")
        return None

class OllamaEngine(AIEngine):
    async def classify(self, text: str) -> Optional[Dict[str, Any]]:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_PASA},
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
                    return self._parse_response(raw_text)
            except Exception as e:
                logger.warning(f"⚠️ [AI] Ollama failure: {e}")
        return None

class AIService:
    def __init__(self, db_client=None):
        self.db = db_client
        self.engines: Dict[str, AIEngine] = {}
        self.cascade_order: List[str] = ["gemini", "groq", "ollama"]
        
        # Auto-registro padrão
        self.register_engine("gemini", GeminiEngine())
        self.register_engine("groq", GroqEngine())
        self.register_engine("ollama", OllamaEngine())

    def register_engine(self, name: str, engine: AIEngine):
        """Registra um novo motor de IA."""
        self.engines[name] = engine
        logger.debug(f"[AI] Motor registrado: {name}")

    async def classify(self, text: str) -> Dict[str, Any]:
        """Classifica texto usando cascata de motores registrada."""
        if not text or not text.strip():
            return {"category": "NEUTRO", "confidence": 1.0, "is_hate": False, "reason": "Input vazio", "engine": "none"}

        start_time = time.perf_counter()
        
        for engine_name in self.cascade_order:
            engine = self.engines.get(engine_name)
            if not engine: continue
            
            result = await engine.classify(text)
            if result:
                result["latency"] = time.perf_counter() - start_time
                result["engine"] = engine_name
                logger.info(f"📊 [AI] {engine_name.upper()} | {result['category']} | {result['latency']:.2f}s")
                return result

        return {
            "category": "NEUTRO", 
            "confidence": 0.0, 
            "is_hate": False, 
            "reason": "Cascata de IA esgotada", 
            "engine": "fail",
            "latency": time.perf_counter() - start_time
        }

    async def run_batch_classification(self, limit: int = 200):
        """Processamento em lote com persistência via DB injetado."""
        if not self.db:
            from core.db import db_client
            self.db = db_client

        comentarios = await self.db.fetch_unprocessed_comments(limit=limit)
        if not comentarios: return 0

        logger.info(f"🧠 [AI] Processando lote de {len(comentarios)} sinais...")
        updates = []
        
        for c in comentarios:
            result = await self.classify(c.get('texto_bruto', ''))
            updates.append({
                "id": c['id'],
                "is_hate": result['is_hate'],
                "categoria_ia": result['category'],
                "confianza_ia": result['confidence'],
                "processado_ia": True
            })

        if updates:
            await self.db.batch_update_comments(updates)
            logger.info(f"💾 [AI] Persistidos {len(updates)} resultados.")
        
        return len(updates)

# Singleton para uso global, mas permite injeção via construtor
ai_service = AIService()
