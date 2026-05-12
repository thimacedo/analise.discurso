
import asyncio
import sys
import os

# Adiciona o diretório raiz ao path para encontrar o pacote core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_service import ai_service

async def reset():
    ai_service.engine_scores = {
        "gemini": 50,
        "groq": 100,
        "ollama": 80
    }
    print("✅ [AI] Scores dos motores resetados para estado de resfriamento.")
    print(f"📊 Estado atual: {ai_service.engine_scores}")

if __name__ == "__main__":
    asyncio.run(reset())
