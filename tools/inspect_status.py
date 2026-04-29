import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def inspect_status():
    headers = {
        "apikey": os.getenv("SUPABASE_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
    }
    url = f"{os.getenv('SUPABASE_URL')}/rest/v1/candidatos?select=username,status_monitoramento&limit=10"
    
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers)
        print(r.json())

if __name__ == "__main__":
    asyncio.run(inspect_status())
