import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SENTINELA_SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

CSV_PATH = r"E:\projetos\sentinela-democratica\data\perfis_consolidados_eleicoes_2026.csv"

def sync_csv_to_db():
    if not os.path.exists(CSV_PATH):
        print(f"❌ Arquivo CSV não encontrado em: {CSV_PATH}")
        return

    print(f"📖 Lendo perfis do CSV: {CSV_PATH}")
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return

    print(f"🔄 Sincronizando {len(df)} perfis para o Supabase...")
    
    count_success = 0
    count_error = 0

    for _, row in df.iterrows():
        username = str(row['username']).strip().replace("@", "")
        data = {
            "username": username,
            "nome_completo": row.get('full_name', row.get('nome', 'Não informado')),
            "cargo": row.get('level', row.get('cargo', 'Monitorado')),
            "estado": row.get('estado', 'N/A'),
            "status_monitoramento": "Ativo"
        }

        url = f"{SUPABASE_URL}/rest/v1/candidatos"
        try:
            res = requests.post(url, headers=HEADERS, json=data)
            if res.status_code in [200, 201]:
                print(f" ✅ @{username} sincronizado.")
                count_success += 1
            else:
                print(f" ❌ Erro @{username}: {res.status_code} - {res.text}")
                count_error += 1
        except Exception as e:
            print(f" ❌ Erro na requisição para @{username}: {e}")
            count_error += 1

    print("\n" + "="*60)
    print(f"✨ Sincronização Concluída!")
    print(f"📊 Sucessos: {count_success}")
    print(f"⚠️ Erros: {count_error}")
    print("="*60)

if __name__ == "__main__":
    sync_csv_to_db()
