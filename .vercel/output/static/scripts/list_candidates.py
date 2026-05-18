import os
import sys
import httpx
from dotenv import load_dotenv

# Força UTF-8 no Windows para evitar UnicodeEncodeError
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,nome_completo"
resp = httpx.get(url, headers=HEADERS)
if resp.status_code == 200:
    data = resp.json()
    print(f"📊 Total de candidatos no banco: {len(data)}")
    for item in data:
        print(f"Handle: @{item['username']} | Nome: {item['nome_completo']}")
else:
    print(f"Erro: {resp.status_code} - {resp.text}")
