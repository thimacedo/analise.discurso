import os
import sys
import httpx
from dotenv import load_dotenv

# Força UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

def inspect_table(table_name):
    print(f"\n🔍 Inspecionando tabela: {table_name}")
    # Busca um registro para ver as colunas
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1"
    try:
        resp = httpx.get(url, headers=HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                print(f"✅ Colunas encontradas: {list(data[0].keys())}")
            else:
                print("⚠️ Tabela vazia.")
        else:
            print(f"❌ Erro ao buscar dados: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    inspect_table("anuncios")
    inspect_table("candidatos")
    inspect_table("comentarios")
