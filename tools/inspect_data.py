import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def inspect_data():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    async with httpx.AsyncClient() as client:
        print("--- Amostra Candidatos ---")
        r = await client.get(f"{url}/rest/v1/candidatos?select=username,status_monitoramento&limit=5", headers=headers)
        print(r.json())
        
        print("\n--- Amostra Comentários ---")
        r = await client.get(f"{url}/rest/v1/comentarios?select=processado_ia,is_hate,texto&limit=5", headers=headers)
        print(r.json())

if __name__ == "__main__":
    asyncio.run(inspect_data())
