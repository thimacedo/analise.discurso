import httpx
import os
import asyncio
import sqlite3
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DB_PATH = "E:/projetos/sentinela-democratica/data/odio_politica.db"

async def sync():
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id_externo, autor_username, texto_bruto FROM comentarios LIMIT 50")
    rows = c.fetchall()
    
    # ID Genérico para teste de persistência
    payload = [{
        "id_externo": f"sync_{r[0]}",
        "autor_username": r[1],
        "texto_bruto": r[2],
        "processado_ia": False,
        "candidato_id": "5fe11fc2-b514-4f48-95ba-28e19f32171f"
    } for r in rows]

    async with httpx.AsyncClient() as client:
        r = await client.post(f"{SUPABASE_URL}/rest/v1/comentarios", headers=headers, json=payload)
        print(f"📊 {len(payload)} evidências sincronizadas. Status: {r.status_code}")
    conn.close()

if __name__ == '__main__':
    asyncio.run(sync())
