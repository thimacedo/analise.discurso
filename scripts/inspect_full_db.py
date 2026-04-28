import os
import httpx
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def inspect():
    async with httpx.AsyncClient() as client:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Prefer": "count=exact"}
        
        tables = ["profiles", "posts", "comments", "comentarios"]
        status = {}
        
        for table in tables:
            try:
                r = await client.get(f"{SUPABASE_URL}/rest/v1/{table}?select=id&limit=1", headers=headers)
                if r.status_code == 200:
                    count = r.headers.get("content-range", "0-0/0").split("/")[-1]
                    status[table] = int(count)
                else:
                    status[table] = f"Error: {r.status_code}"
            except Exception as e:
                status[table] = str(e)
        
        print(json.dumps(status, indent=2))

if __name__ == "__main__":
    asyncio.run(inspect())
