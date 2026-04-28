import sqlite3
import os
import asyncio
from core.ai_engine import AIEngine

DB_PATH = "E:/projetos/sentinela-democratica/data/odio_politica.db"
load_dotenv() # GROQ_API_KEY from .env

async def process_full_backlog():
    print("?? [INTELLIGENCE] Limpando backlog local...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    engine = AIEngine()
    while True:
        c.execute("SELECT id, texto_bruto FROM comentarios WHERE processado_ia = 0 LIMIT 10")
        rows = c.fetchall()
        if not rows: break

        for row_id, texto in rows:
            try:
                res = await engine.analyze_comment(texto)
                c.execute("UPDATE comentarios SET processado_ia = 1, is_hate = ?, categoria_ia = ? WHERE id = ?",
                          (1 if res.get('is_hate') else 0, res.get('categoria', 'NEUTRO'), row_id))
                print(f"[{row_id}] -> {res.get('categoria', 'NEUTRO')}")
            except Exception as e:
                print(f"? Erro no ID {row_id}: {e}")
                await asyncio.sleep(5)
        
        conn.commit()
        await asyncio.sleep(1)

    conn.close()
    print("?? Backlog processado.")

if __name__ == '__main__':
    asyncio.run(process_full_backlog())
