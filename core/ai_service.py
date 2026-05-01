import json
import httpx
import asyncio
import time
from typing import Dict, Any, Optional
from core.config import settings

SYSTEM_PROMPT_PASA = """
Você é um analista forense do sistema Sentinela Democrática. Classifique o texto segundo o Protocolo PASA v16.4.

CATEGORIAS EXATAS (Não invente outras):
- NEUTRO (Críticas políticas, protestos, apoios agressivos, debates ideológicos NÃO são ódio).
- ODIO_IDENTITARIO (Xenofobia, racismo, regionalismo pejorativo).
- VIOLENCIA_GENERO (Misoginia, ofensas à condição feminina).
- AMEACA (Incitação a dano físico ou morte).
- INSULTO_AD_HOMINEM (Desumanização: lixo, rato, verme, escória).
- ATAQUE_INSTITUCIONAL (Deslegitimação de órgãos como STF/TSE).
- RIGOR_CRIMINAL (Imputação de crime sem prova: ladrão, corrupto, bandido).

⚠️ CUIDADO: Cartas abertas, posicionamentos políticos e reclamações de gestão devem ser classificados como NEUTRO.

REGRAS DE SAÍDA:
1. Responda APENAS com um JSON válido.
2. Formato: {"category": "CATEGORIA", "confidence": 0.95, "is_hate": true, "reason": "breve motivo"}
"""

class AIService:
    def __init__(self):
        self.provider = settings.IA_PROVIDER
        self.consecutive_failures = 0
        self.max_failures = 3
        self.current_engine = self._determine_initial_engine()

    def _determine_initial_engine(self):
        if settings.GEMINI_API_KEY: return "gemini"
        if settings.GROQ_API_KEY: return "groq"
        return "ollama"

    def _parse_response(self, text: str) -> Dict[str, Any]:
        try:
            clean_text = text.strip().replace('```json', '').replace('```', '')
            data = json.loads(clean_text)
            
            category = str(data.get("category") or data.get("categoria", "NEUTRO")).upper().strip()
            # Correção de typos comuns
            if category == "ODEIO_IDENTITARIO": category = "ODIO_IDENTITARIO"
            
            valid_categories = ["NEUTRO", "ODIO_IDENTITARIO", "VIOLENCIA_GENERO", "AMEACA", "INSULTO_AD_HOMINEM", "ATAQUE_INSTITUCIONAL", "RIGOR_CRIMINAL"]
            if category not in valid_categories:
                category = "NEUTRO"
                
            return {
                "category": category,
                "confidence": float(data.get("confidence") or data.get("confianza") or data.get("confianca", 0.0)),
                "is_hate": bool(data.get("is_hate", False)),
                "reason": data.get("reason") or data.get("justificativa", "")
            }
        except Exception:
            return {"category": "NEUTRO", "confidence": 0.0, "is_hate": False, "reason": "Erro no processamento da resposta"}

    async def _call_gemini(self, text: str) -> Optional[Dict[str, Any]]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
        payload = {
            "contents": [{"parts": [{"text": f"{SYSTEM_PROMPT_PASA}\n\nTEXTO: \"{text}\""}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=20.0)
                if resp.status_code == 200:
                    content = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    return self._parse_response(content)
            except Exception as e:
                print(f"⚠️ Gemini Error: {e}")
        return None

    async def _call_groq(self, text: str) -> Optional[Dict[str, Any]]:
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
                resp = await client.post(url, headers=headers, json=payload, timeout=20.0)
                if resp.status_code == 200:
                    content = resp.json()['choices'][0]['message']['content']
                    return self._parse_response(content)
            except Exception as e:
                print(f"⚠️ Groq Error: {e}")
        return None

    async def _call_ollama(self, text: str) -> Dict[str, Any]:
        url = f"{settings.OLLAMA_BASE_URL}/api/generate"
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": f"{SYSTEM_PROMPT_PASA}\n\nTEXTO: \"{text}\"",
            "stream": False,
            "format": "json"
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, timeout=60.0)
                if resp.status_code == 200:
                    content = resp.json().get("response", "{}")
                    return self._parse_response(content)
            except Exception as e:
                print(f"⚠️ Ollama Error: {e}")
        return {"category": "NEUTRO", "confidence": 0.0, "is_hate": False, "reason": "Ollama falhou"}

    async def classify(self, text: str) -> Dict[str, Any]:
        if not text or not text.strip():
            return {"category": "NEUTRO", "confidence": 1.0, "is_hate": False, "reason": "Texto vazio"}

        result = None
        
        # Tenta motor atual
        if self.current_engine == "gemini":
            result = await self._call_gemini(text)
            if not result: self.current_engine = "groq"
            
        if not result and self.current_engine == "groq":
            result = await self._call_groq(text)
            if not result:
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.max_failures:
                    self.current_engine = "ollama"
            else:
                self.consecutive_failures = 0
                
        if not result:
            result = await self._call_ollama(text)
            
        return result

    async def query(self, prompt: str, system_prompt: str = "Você é um assistente prestativo.") -> str:
        """Consulta genérica à IA com fallback."""
        # Tenta Gemini
        if settings.GEMINI_API_KEY:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
                payload = {"contents": [{"parts": [{"text": f"{system_prompt}\n\n{prompt}"}]}]}
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, json=payload, timeout=30.0)
                    if resp.status_code == 200:
                        return resp.json()['candidates'][0]['content']['parts'][0]['text']
            except: pass

        # Tenta Groq
        if settings.GROQ_API_KEY:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
                payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]}
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, headers=headers, json=payload, timeout=25.0)
                    if resp.status_code == 200:
                        return resp.json()['choices'][0]['message']['content']
            except: pass

        # Tenta Ollama
        try:
            url = f"{settings.OLLAMA_BASE_URL}/v1/chat/completions"
            payload = {"model": settings.OLLAMA_MODEL, "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "stream": False}
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=30.0)
                if resp.status_code == 200:
                    return resp.json()['choices'][0]['message']['content']
        except: pass

        return ""

async def run_batch_classification(limit: int = 200):
    """Executa processamento de IA em lote utilizando o DatabaseClient e AIService."""
    from core.db import db_client
    
    print(f"🧠 Intelligence Engine: Motor atual: {ai_service.current_engine}")
    
    comentarios = await db_client.fetch_unprocessed_comments(limit=limit)
    if not comentarios:
        print("✅ Tudo processado.")
        return 0

    total = len(comentarios)
    print(f"📦 Processando lote de {total} comentários pendentes.")
    updates = []
    
    for i, c in enumerate(comentarios, 1):
        text = c.get('texto_bruto', '')
        result = await ai_service.classify(text)
        
        updates.append({
            "id": c['id'],
            "is_hate": result['is_hate'],
            "categoria_ia": result['category'],
            "confianza_ia": result['confidence'],
            "processado_ia": True
        })
        
        icon = "🔥" if result['is_hate'] else "✅"
        print(f"   [{i}/{total}] {icon} @{c.get('autor_username')}: {result['category']}")

    if updates:
        await db_client.batch_update_comments(updates)
        print(f"💾 Persistidos {len(updates)} resultados.")
    
    return len(updates)

ai_service = AIService()
