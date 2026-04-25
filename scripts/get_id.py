import os
import requests

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "SUPABASE_KEY_PLACEHOLDER")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}" }

def get_any_id():
    url = f"{SUPABASE_URL}/rest/v1/candidatos?limit=1&select=id,username"
    res = requests.get(url, headers=HEADERS)
    print(res.json())

if __name__ == "__main__":
    get_any_id()
