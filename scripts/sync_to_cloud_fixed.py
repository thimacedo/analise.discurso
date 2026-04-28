import httpx
import os
import asyncio
import sqlite3
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY")

async def sync():
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    conn = sqlite3.connect("E:/projetos/sentinela-democratica/data/odio_politica.db")
    c = conn.cursor()
    c.execute("SELECT id_externo, autor_username, texto_bruto, post_id FROM comentarios WHERE texto_bruto IS NOT NULL LIMIT 50")
    rows = c.fetchall()
    
    payload = [{
        "id_externo": f"sync_{r[0]}",
        "autor_username": r[1] or "anonimo",
        "texto_bruto": r[2],
        "post_id": r[3] or "legacy_post",
        "candidato_id": "5fe11fc2-b514-4f48-95ba-28e19f32171f",
        "processado_ia": False
    } for r in rows]

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{SUPABASE_URL}/rest/v1/comentarios", headers=headers, json=payload)
        print(f"✅ {len(payload)} evidências históricas sincronizadas (Status: {r.status_code})")
    conn.close()

if __name__ == '__main__':
    asyncio.run(sync())
