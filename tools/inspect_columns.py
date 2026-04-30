import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def inspect_columns():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{url}/rest/v1/candidatos?limit=1", headers=headers)
        if r.status_code == 200 and r.json():
            print(f"Colunas de candidatos: {list(r.json()[0].keys())}")
        else:
            print(f"Erro ou sem dados: {r.status_code} - {r.text}")

if __name__ == "__main__":
    asyncio.run(inspect_columns())
