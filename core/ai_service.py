import json
import httpx
import asyncio
import time
import logging
import traceback
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
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

class AIService:
    def __init__(self):
        self.provider = settings.IA_PROVIDER
        self.engines = {
            "gemini": self._call_gemini,
            "groq": self._call_groq,
            "ollama": self._call_ollama
        }
        # Ordem de tentativa baseada no provider
        self.cascade_order = self._get_cascade_order()

    def _get_cascade_order(self) -> List[str]:
        if self.provider == "ollama": return ["ollama", "gemini", "groq"]
        if self.provider == "groq": return ["groq", "gemini", "ollama"]
        return ["gemini", "groq", "ollama"]

    def _parse(self, text: str) -> Dict[str, Any]:
        """Parser resiliente para respostas de IA."""
        try:
            clean = text.strip().replace('```json', '').replace('```', '')
            data = json.loads(clean)
            cat = str(data.get("category", "NEUTRO")).upper().replace("ODEIO", "ODIO").strip()
            
            valid = ["NEUTRO", "ODIO_IDENTITARIO", "VIOLENCIA_GENERO", "AMEACA", "INSULTO_AD_HOMINEM", "ATAQUE_INSTITUCIONAL", "RIGOR_CRIMINAL"]
            if cat not in valid: cat = "NEUTRO"
            
            return {
                "category": cat,
                "confidence": float(data.get("confidence", 0.0)),
                "is_hate": bool(data.get("is_hate", False)),
                "reason": data.get("reason", "Análise automatizada")
            }
        except:
            return {"category": "NEUTRO", "confidence": 0.0, "is_hate": False, "reason": "Erro de processamento"}

    async def _call_gemini(self, text: str) -> Optional[Dict]:
        if not settings.GEMINI_API_KEY: return None
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": f"{SYSTEM_PROMPT_PASA}\n\nTEXTO: \"{text}\""}]}], "generationConfig": {"response_mime_type": "application/json"}}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    return self._parse(resp.json()['candidates'][0]['content']['parts'][0]['text'])
            except Exception as e: logger.warning(f"[AI] Gemini failure: {e}")
        return None

    async def _call_groq(self, text: str) -> Optional[Dict]:
        if not settings.GROQ_API_KEY: return None
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
        payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": SYSTEM_PROMPT_PASA}, {"role": "user", "content": f"TEXTO: \"{text}\""}], "response_format": {"type": "json_object"}}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, headers=headers, json=payload, timeout=15.0)
                if resp.status_code == 200:
                    return self._parse(resp.json()['choices'][0]['message']['content'])
            except Exception as e: logger.warning(f"[AI] Groq failure: {e}")
        return None

    async def _call_ollama(self, text: str) -> Optional[Dict]:
        url = f"{settings.OLLAMA_BASE_URL}/api/chat"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT_PASA}, {"role": "user", "content": f"TEXTO: \"{text}\""}],
            "stream": False, "format": "json", "options": {"temperature": 0.1}
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=30.0)
                if resp.status_code == 200:
                    return self._parse(resp.json().get("message", {}).get("content", ""))
            except Exception as e: logger.warning(f"[AI] Ollama failure: {e}")
        return None

    async def classify(self, text: str) -> Dict[str, Any]:
        """Classifica texto usando cascata de provedores."""
        if not text or not text.strip():
            return {"category": "NEUTRO", "confidence": 1.0, "is_hate": False, "reason": "Input vazio", "engine": "none"}

        start = time.perf_counter()
        for engine_name in self.cascade_order:
            method = self.engines.get(engine_name)
            if not method: continue
            
            result = await method(text)
            if result:
                result["latency"] = time.perf_counter() - start
                result["engine"] = engine_name
                logger.info(f"📊 [AI] {engine_name.upper()} | {result['category']} | {result['latency']:.2f}s")
                return result

        return {"category": "NEUTRO", "confidence": 0.0, "is_hate": False, "reason": "Cascata de IA esgotada", "engine": "fail"}

    async def query(self, prompt: str, system: str = "Assistente Sentinela.") -> str:
        """Consulta genérica ultra-resiliente."""
        # Implementação simplificada usando apenas o primeiro disponível da cascata
        for engine in self.cascade_order:
            if engine == "gemini" and settings.GEMINI_API_KEY:
                try:
                    res = await self._call_gemini(f"{system}\n\n{prompt}")
                    if res: return res.get("reason", "")
                except: pass
            # ... fallback para outros se necessário, mas foco é o PASA
        return "Erro na consulta estratégica."

async def run_batch_classification(limit: int = 200):
    """Processamento de IA em lote (Diamond Style)."""
    from core.db import db_client
    
    comentarios = await db_client.fetch_unprocessed_comments(limit=limit)
    if not comentarios: return 0

    logger.info(f"🧠 [AI] Processando lote de {len(comentarios)} sinais...")
    updates = []
    
    for c in comentarios:
        result = await ai_service.classify(c.get('texto_bruto', ''))
        updates.append({
            "id": c['id'],
            "is_hate": result['is_hate'],
            "categoria_ia": result['category'],
            "confianza_ia": result['confidence'],
            "processado_ia": True
        })

    if updates:
        await db_client.batch_update_comments(updates)
        logger.info(f"💾 [AI] Persistidos {len(updates)} resultados.")
    
    return len(updates)

ai_service = AIService()
