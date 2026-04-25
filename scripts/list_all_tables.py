import os
import requests

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "SUPABASE_KEY_PLACEHOLDER")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}" }

def list_all():
    url = f"{SUPABASE_URL}/rest/v1/"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        defs = res.json().get('definitions', {})
        for d in defs:
            print(f"Table: {d}")
    else:
        print(f"Error: {res.status_code}")

if __name__ == "__main__":
    list_all()
