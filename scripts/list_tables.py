import os
import requests

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

def list_tables():
    # Consultar o Postgrest para listar tabelas disponíveis
    url = f"{SUPABASE_URL}/rest/v1/"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        print("📋 Tabelas encontradas:")
        for table in data.get('definitions', {}).keys():
            print(f"  - {table}")
    else:
        print(f"❌ Erro ao listar tabelas: {response.status_code} - {response.text}")

if __name__ == "__main__":
    list_tables()
