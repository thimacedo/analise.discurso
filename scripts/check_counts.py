import os
import requests

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}" }

def check_counts():
    url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,comentarios_totais_count,comentarios_odio_count&limit=10"
    res = requests.get(url, headers=HEADERS)
    print(res.json())

if __name__ == "__main__":
    check_counts()
