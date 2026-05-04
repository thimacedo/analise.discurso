import pytest
import asyncio
import sys
import os

# Adiciona o diretório raiz ao path para importar core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_service import AIService, AIEngine
from typing import Optional, Dict, Any

class MockEngine(AIEngine):
    def __init__(self, name, should_fail=False):
        self.name = name
        self.should_fail = should_fail

    async def classify(self, text: str) -> Optional[Dict[str, Any]]:
        if self.should_fail:
            return None
        return {
            "category": "NEUTRO",
            "confidence": 0.99,
            "is_hate": False,
            "reason": f"Mocked response from {self.name}"
        }

@pytest.mark.asyncio
async def test_cascade_logic():
    # 1. Teste de Sucesso no Primeiro Motor (Gemini)
    service = AIService()
    service.register_engine("gemini", MockEngine("Gemini"))
    service.register_engine("groq", MockEngine("Groq"))
    service.register_engine("ollama", MockEngine("Ollama"))
    
    res = await service.classify("Teste 1")
    assert res['engine'] == 'gemini'

    # 2. Teste de Fallback para Groq
    service = AIService()
    service.register_engine("gemini", MockEngine("Gemini", should_fail=True))
    service.register_engine("groq", MockEngine("Groq"))
    service.register_engine("ollama", MockEngine("Ollama"))
    
    res = await service.classify("Teste 2")
    assert res['engine'] == 'groq'

    # 3. Teste de Fallback para Ollama
    service = AIService()
    service.register_engine("gemini", MockEngine("Gemini", should_fail=True))
    service.register_engine("groq", MockEngine("Groq", should_fail=True))
    service.register_engine("ollama", MockEngine("Ollama"))
    
    res = await service.classify("Teste 3")
    assert res['engine'] == 'ollama'

    # 4. Teste de Falha Total
    service = AIService()
    service.register_engine("gemini", MockEngine("Gemini", should_fail=True))
    service.register_engine("groq", MockEngine("Groq", should_fail=True))
    service.register_engine("ollama", MockEngine("Ollama", should_fail=True))
    
    res = await service.classify("Teste 4")
    assert res['engine'] == 'fail'
