import os
import httpx
import json
import sys
from dotenv import load_dotenv

load_dotenv()

# Configuração do Qwen Local Hub
QWEN_ENDPOINT = os.getenv("QWEN_ENDPOINT", "http://localhost:11434/v1/chat/completions")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen2.5-coder:7b")

async def query_qwen(prompt, system_prompt="Você é um engenheiro de software sênior especializado em Qwen."):
    """Consulta o modelo Qwen local para tarefas de programação de baixa latência."""
    payload = {
        "model": QWEN_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(QWEN_ENDPOINT, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Erro Local Hub: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Falha de conexão com Qwen Local Hub: {e}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python query_qwen.py 'seu prompt aqui'")
        sys.exit(1)
    
    import asyncio
    user_prompt = sys.argv[1]
    print(asyncio.run(query_qwen(user_prompt)))
