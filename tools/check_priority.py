
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import httpx
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

async def check_priority():
    with open("data/priority_queue.json", "r") as f:
        priority = json.load(f)
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    async with httpx.AsyncClient() as client:
        print(f"--- Verificando Prioridade ({len(priority)} perfis) ---")
        for username in priority:
            r = await client.get(f"{url}/rest/v1/candidatos?username=eq.{username}&select=username,last_scraped_at", headers=headers)
            data = r.json()
            if data:
                status = data[0].get('last_scraped_at') or "NUNCA"
                print(f"@{username}: {status}")
            else:
                print(f"@{username}: NÃO ENCONTRADO NO DB")

if __name__ == "__main__":
    asyncio.run(check_priority())
