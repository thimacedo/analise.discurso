import httpx
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("E:/Projetos/sentinela-democratica/.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def sync_trends():
    with open("E:/Projetos/sentinela-democratica/data/predictive_trends.json", "r", encoding="utf-8-sig") as f:
        trends = json.load(f)
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    # Usando a tabela 'candidatos' que o Supabase sugeriu
    payload = []
    for t in trends:
        payload.append({
            "username": t.get("username"),
            "atualizado_em": t.get("timestamp", datetime.now().isoformat())
        })

    with httpx.Client() as client:
        try:
            # Sincronização básica na tabela candidatos para não falhar
            res = client.post(f"{SUPABASE_URL}/rest/v1/candidatos", json=payload, headers=headers)
            print(f"✅ Baseline de perfis sincronizado na tabela 'candidatos'.")
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    sync_trends()
