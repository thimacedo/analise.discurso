import sqlite3
import httpx
import os
import asyncio
import json

DB_PATH = "E:/projetos/sentinela-democratica/data/odio_politica.db"
GEMINI_KEY = "AIzaSyD_u4MnON2QY-eXnBZRMCC3-cyYvXQSjMc"

async def analyze_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    prompt = f"Analise pericialmente (PASA v15.5): '{text}'. Retorne JSON: {{'is_hate': bool, 'categoria': 'string'}}"
    
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=20.0)
            if res.status_code == 200:
                raw = res.json()['candidates'][0]['content']['parts'][0]['text']
                # Extrai JSON de blocos de código se houver
                if "`json" in raw:
                    raw = raw.split("`json")[1].split("`")[0]
                return json.loads(raw)
        except: pass
    return {"is_hate": False, "categoria": "NEUTRO"}

async def run():
    print("💎 [GEMINI CONTINGENCY] Processando backlog...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, texto_bruto FROM comentarios WHERE processado_ia = 0 LIMIT 10")
    rows = c.fetchall()
    
    for rid, texto in rows:
        print(f"[-] Analisando ID {rid}...")
        res = await analyze_gemini(texto)
        c.execute("UPDATE comentarios SET processado_ia = 1, is_hate = ?, categoria_ia = ? WHERE id = ?",
                  (1 if res.get('is_hate') else 0, res.get('categoria', 'NEUTRO'), rid))
        print(f"✅ Veredito: {res.get('categoria')}")
    
    conn.commit()
    conn.close()
    print("🏁 Backlog atualizado.")

if __name__ == '__main__':
    asyncio.run(run())
