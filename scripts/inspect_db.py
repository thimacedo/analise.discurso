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

# Verifica se a tabela profiles existe e tem stn_tokens
url_profiles = f"{SUPABASE_URL}/rest/v1/profiles?select=stn_tokens&limit=1"
resp_profiles = httpx.get(url_profiles, headers=HEADERS)
if resp_profiles.status_code == 200:
    print("✅ Tabela 'profiles' ok.")
    print(f"Dados: {resp_profiles.json()}")
else:
    print(f"❌ Tabela 'profiles' erro: {resp_profiles.status_code} - {resp_profiles.text}")
