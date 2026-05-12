
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
HEADERS = {"apikey": KEY, "Authorization": f"Bearer {KEY}"}

def inspect(table):
    resp = httpx.get(f"{URL}/rest/v1/{table}?limit=1", headers=HEADERS)
    if resp.status_code == 200:
        data = resp.json()
        print(f"📊 {table}: {list(data[0].keys()) if data else 'Vazia'}")
    else:
        print(f"❌ {table}: {resp.status_code}")

if __name__ == "__main__":
    tables = [
        "dashboard_intel_agregada",
        "dashboard_comentarios_classificacao",
        "historico_monitoramento",
        "scraping_accounts"
    ]
    for t in tables:
        inspect(t)
