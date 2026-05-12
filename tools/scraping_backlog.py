
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import httpx
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

async def get_scraping_backlog():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Prefer": "count=exact"}
    
    cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()
    
    async with httpx.AsyncClient() as client:
        # Nunca raspados
        r_null = await client.get(f"{url}/rest/v1/candidatos?last_scraped_at=is.null&select=id", headers=headers)
        null_count = r_null.headers.get("Content-Range", "0-0/0").split("/")[-1]
        
        # Raspagem antiga (> 24h)
        r_old = await client.get(f"{url}/rest/v1/candidatos?last_scraped_at=lt.{cutoff}&select=id", headers=headers)
        old_count = r_old.headers.get("Content-Range", "0-0/0").split("/")[-1]
        
        print(f"🕵️ BACKLOG DE RASPAGEM")
        print(f"----------------------")
        print(f"Candidatos NUNCA raspados: {null_count}")
        print(f"Candidatos com raspagem atrasada (>24h): {old_count}")

if __name__ == "__main__":
    asyncio.run(get_scraping_backlog())
