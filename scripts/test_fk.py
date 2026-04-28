import os
import requests
import json
import uuid
from datetime import datetime

# Configurações do Supabase
SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "SUPABASE_KEY_PLACEHOLDER")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json" }

def test_fk():
    cand_id = "e67826ae-298a-4f95-a907-92eb5cfe3df4"
    dummy_uuid = str(uuid.uuid4())
    data = {
        "candidato_id": cand_id,
        "post_id": dummy_uuid,
        "id_externo": dummy_uuid,
        "texto_bruto": "Teste FK",
        "categoria_ia": "Odio",
        "is_hate": True,
        "data_coleta": datetime.now().isoformat(),
        "data_publicacao": datetime.now().isoformat()
    }
    url = f"{SUPABASE_URL}/rest/v1/comentarios"
    res = requests.post(url, headers=HEADERS, json=data)
    print(res.text)

if __name__ == "__main__":
    test_fk()
