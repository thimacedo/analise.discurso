import os
import requests
import json
import uuid
from datetime import datetime

# Configurações do Supabase
SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "SUPABASE_KEY_PLACEHOLDER")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json" }

def debug_db():
    # 1. Inserir Candidato de Teste
    new_id = str(uuid.uuid4())
    cand_data = {
        "id": new_id,
        "username": "test_bot_" + str(int(datetime.now().timestamp())),
        "nome_completo": "Test Bot",
        "status_monitoramento": "Ativo"
    }
    print(f"🛠️ Criando candidato {new_id}...")
    res_c = requests.post(f"{SUPABASE_URL}/rest/v1/candidatos", headers=HEADERS, json=cand_data)
    print(f"Candidato: {res_c.status_code}")
    
    if res_c.status_code in [200, 201]:
        # 2. Tentar inserir comentário
        comm_data = {
            "candidato_id": new_id,
            "post_id": new_id, # Usando o mesmo UUID como dummy
            "id_externo": new_id,
            "texto_bruto": "Alerta Crítico de Teste",
            "categoria_ia": "Odio",
            "is_hate": True,
            "data_coleta": datetime.now().isoformat()
        }
        print(f"🛠️ Criando comentário para {new_id}...")
        res_m = requests.post(f"{SUPABASE_URL}/rest/v1/comentarios", headers=HEADERS, json=comm_data)
        print(f"Comentário: {res_m.status_code} - {res_m.text}")

if __name__ == "__main__":
    debug_db()
