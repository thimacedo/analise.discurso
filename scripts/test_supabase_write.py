import os
import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def force_test():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    test_data = {
        "id_externo": f"TEST_{int(datetime.now().timestamp())}",
        "candidato_id": "BRAINTRUST_TEST_NODE",
        "post_id": "TEST_POST",
        "autor_username": "debug_agent",
        "texto_bruto": "🚨 TESTE DE FLUXO ATIVO: Se você está vendo isso, a conexão com o Supabase está OK!",
        "data_coleta": datetime.now().isoformat(),
        "is_hate": True,
        "categoria_ia": "[GROQ-70B] TEST_LINK",
        "processado_ia": True,
        "user_id": "66f853ed-c42b-43d4-bcc3-23f05b2c44e9"
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{url}/rest/v1/comentarios", json=test_data, headers=headers)
        print(f"Status: {r.status_code}")
        print(f"Resposta: {r.text}")

if __name__ == "__main__":
    asyncio.run(force_test())
