import os
import requests
import json
import uuid
from datetime import datetime

# Configurações do Supabase
SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "SUPABASE_KEY_PLACEHOLDER")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json" }

def inject_test_alerts():
    # Comentários Reais Extraídos agora do Apify
    alertas = [
        {"texto_bruto": "Voce é o maior mentiroso do Brasil e está sempre contra os trabalhadores. Lula presidente no primeiro turno", "candidato_id": "nikolasferreiradm", "categoria_ia": "Odio", "is_hate": True},
        {"texto_bruto": "Trabalhar que é bom... Nada né? Chupetinha! Kkkk", "candidato_id": "nikolasferreiradm", "categoria_ia": "Odio", "is_hate": True},
        {"texto_bruto": "Um bom deputado até cagar na saída😂 é contra escala 6x1 pq nunca foi clt", "candidato_id": "nikolasferreiradm", "categoria_ia": "Odio", "is_hate": True},
        {"texto_bruto": "Se for na missa vai ser expulso", "candidato_id": "nikolasferreiradm", "categoria_ia": "Odio", "is_hate": True}
    ]

    print(f"🚀 Injetando {len(alertas)} alertas reais para @nikolasferreiradm...")
    
    url = f"{SUPABASE_URL}/rest/v1/comentarios"
    for a in alertas:
        data = {
            "candidato_id": a['candidato_id'],
            "post_id": "manual_injection",
            "id_externo": str(uuid.uuid4()),
            "texto_bruto": a['texto_bruto'],
            "categoria_ia": a['categoria_ia'],
            "is_hate": a['is_hate'],
            "data_coleta": datetime.now().isoformat(),
            "data_publicacao": datetime.now().isoformat()
        }
        res = requests.post(url, headers=HEADERS, json=data)
        if res.status_code in [200, 201]:
            print(f" ✅ Alerta injetado: {a['texto_bruto'][:30]}...")
        else:
            print(f" ❌ Erro: {res.text}")

if __name__ == "__main__":
    inject_test_alerts()
