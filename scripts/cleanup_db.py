import sqlite3
import httpx
import asyncio
import os

DB_PATH = "E:/projetos/sentinela-democratica/data/odio_politica.db"
SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY"

async def cleanup():
    # 1. Limpeza Local
    print("🧹 Iniciando saneamento local...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    patterns = ['DEBUG_%', 'TEST_%', 'FORCE_%', 'bb_control%', 'local_%', 'sync_%']
    total_local = 0
    for p in patterns:
        c.execute("DELETE FROM comentarios WHERE id_externo LIKE ?", (p,))
        total_local += c.rowcount
    conn.commit()
    conn.close()
    print(f"✅ {total_local} registros sintéticos removidos localmente.")

    # 2. Limpeza Cloud (Supabase)
    print("☁️ Iniciando saneamento na nuvem...")
    h = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}"}
    async with httpx.AsyncClient() as client:
        # Padrões de deleção via Query Params
        for p in ['DEBUG', 'TEST', 'FORCE', 'bb_control', 'local', 'sync']:
            r = await client.delete(f"{SB_URL}/comentarios?id_externo=like.{p}*", headers=h)
            print(f"[-] Removendo padrão {p} na nuvem: {r.status_code}")
    
    print("🏁 Banco de dados limpo. Apenas evidências reais preservadas.")

if __name__ == '__main__':
    asyncio.run(cleanup())
