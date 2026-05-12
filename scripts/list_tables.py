
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

def list_tables():
    headers = {
        "apikey": KEY,
        "Authorization": f"Bearer {KEY}"
    }
    resp = httpx.get(f"{URL}/rest/v1/", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        tables = data.get("definitions", {}).keys()
        print("📋 Tabelas detectadas via API:")
        for t in tables:
            print(f" - {t}")
    else:
        print(f"❌ Erro: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    list_tables()
