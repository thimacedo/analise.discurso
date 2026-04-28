import os
import requests

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "SUPABASE_KEY_PLACEHOLDER")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}" }

def check_existing_comments():
    url = f"{SUPABASE_URL}/rest/v1/comentarios?limit=5&select=candidato_id"
    res = requests.get(url, headers=HEADERS)
    print(res.json())

if __name__ == "__main__":
    check_existing_comments()
