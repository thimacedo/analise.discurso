import os
import requests

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "SUPABASE_KEY_PLACEHOLDER")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}" }

def inspect_agregada():
    url = f"{SUPABASE_URL}/rest/v1/dashboard_intel_agregada"
    params = {"limit": 1}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()
        print("🔍 Colunas de 'dashboard_intel_agregada':")
        if data:
            print(data[0].keys())
        else:
            print("Tabela vazia.")
    else:
        print(f"❌ Erro: {response.status_code}")

if __name__ == "__main__":
    inspect_agregada()
