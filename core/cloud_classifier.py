import os
import httpx
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def run_cloud_classification():
    print("🧠 Classificador v3.1: Refinando detecção...")
    
    # Busca apenas o que ainda não foi processado
    url_fetch = f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.false&limit=50"
    try:
        resp = httpx.get(url_fetch, headers=HEADERS)
        comments = resp.json()
        
        if not comments:
            print("✅ Nada novo para processar.")
            return

        for c in comments:
            text = c.get("texto_bruto", "")
            comment_id = c.get("id")
            
            # LÓGICA REFINADA
            is_hate, category = refine_classify(text)
            
            # 2. Atualiza no Supabase com o veredito real
            url_update = f"{SUPABASE_URL}/rest/v1/comentarios?id=eq.{comment_id}"
            update_data = {
                "processado_ia": True,
                "is_hate": is_hate,
                "categoria_ia": category,
                "texto_limpo": text.lower().strip()
            }
            
            httpx.patch(url_update, json=update_data, headers=HEADERS)
            print(f"   [{category}] @{c.get('autor_username')}: {text[:30]}...")

    except Exception as e:
        print(f"❌ Erro: {e}")

def refine_classify(text):
    text_lower = text.lower()
    
    # 1. Ignorar aplausos e emojis positivos
    positive_vibes = ['👏', '🔥', '🙌', 'parabens', 'sucesso', 'apoio', 'deus abencoe', 'tmj']
    for word in positive_vibes:
        if word in text_lower:
            return False, "NEUTRO/APOIO"

    # 2. Palavras de ódio real (Agressão direta)
    hate_words = ['lixo', 'vagabundo', 'idiota', 'corrupto', 'morra', 'assassino']
    for word in hate_words:
        if word in text_lower:
            # Verifica contexto de causa animal (Ex: "matar os bichinhos" em tom de denúncia)
            if 'bicho' in text_lower or 'animal' in text_lower:
                return False, "DENÚNCIA/CAUSA ANIMAL"
            return True, "AGRESSÃO/ÓDIO"
            
    return False, "NEUTRO"

if __name__ == "__main__":
    run_cloud_classification()
