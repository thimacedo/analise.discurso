import os
import requests

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

def inspect_candidatos():
    url = f"{SUPABASE_URL}/rest/v1/candidatos"
    params = {"limit": 1}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        data = response.json()
        print("🔍 Estrutura de 'candidatos':")
        if data:
            print(data[0].keys())
        else:
            print("Tabela vazia.")
    else:
        print(f"❌ Erro: {response.status_code}")

if __name__ == "__main__":
    inspect_candidatos()
