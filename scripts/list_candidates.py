import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,nome_completo&limit=50"
resp = httpx.get(url, headers=HEADERS)
if resp.status_code == 200:
    for item in resp.json():
        print(f"Handle: @{item['username']} | Nome: {item['nome_completo']}")
else:
    print(f"Erro: {resp.status_code} - {resp.text}")
