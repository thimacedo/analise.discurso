import os
import httpx
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÕES CLOUD
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") # SERVICE ROLE para escrita
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def run_cloud_classification():
    print("🧠 Iniciando Classificação IA Forense (Cloud Sync)...")
    
    # 1. Busca comentários não processados
    url_fetch = f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.false&limit=20"
    try:
        resp = httpx.get(url_fetch, headers=HEADERS)
        comments = resp.json()
        
        if not comments:
            print("✅ Todos os comentários atuais já foram processados.")
            return

        print(f"🧐 Analisando lote de {len(comments)} comentários...")

        for c in comments:
            text = c.get("texto_bruto", "")
            comment_id = c.get("id")
            
            # SIMULAÇÃO DE CLASSIFICAÇÃO (A ser substituído pelo modelo real BERT/Qwen)
            # Aqui entra a lógica do seu hate_classifier.py
            is_hate, category = dummy_classify(text)
            
            # 2. Atualiza no Supabase
            url_update = f"{SUPABASE_URL}/rest/v1/comentarios?id=eq.{comment_id}"
            update_data = {
                "processado_ia": True,
                "texto_limpo": text.lower().strip(), # Exemplo de limpeza simples
            }
            # Se for ódio, podemos registrar em uma tabela de classificações ou no próprio campo (ajustando schema se necessário)
            # Por enquanto, marcamos como processado para o Dashboard refletir
            
            httpx.patch(url_update, json=update_data, headers=HEADERS)
            print(f"   ✅ Processado: @{c.get('autor_username')} -> {'🚩 ÓDIO' if is_hate else '✅ SEGURO'}")

    except Exception as e:
        print(f"❌ Erro na classificação: {e}")

def dummy_classify(text):
    """Simulação de lógica pericial (Substituir por modelo real)"""
    keywords_odio = ['lixo', 'morra', 'matar', 'vagabundo', 'idiota', 'corrupto']
    for word in keywords_odio:
        if word in text.lower():
            return True, "INSULTO/ÓDIO"
    return False, "NEUTRO"

if __name__ == "__main__":
    run_cloud_classification()
