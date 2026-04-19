import os
import sys
import json
import time
from datetime import datetime, timedelta

# Configuração de caminhos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from collectors.full_apify_scraper import ApifyFullScraper

# Configurações
STATE_FILE = "data/collection_state.json"
PROFILES_FILE = "data/perfis_monitorados.json"
PROFILES_PER_RUN = 15  # 15 perfis por turno (2x ao dia = 30 perfis/dia)
POSTS_PER_PROFILE = 5
COMMENTS_PER_POST = 50

def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def run_orchestrated_collection():
    print(f"🕵️ ORQUESTRADOR MASSIVO v5.8 - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 1. Carregar dados
    profiles = load_json(PROFILES_FILE)
    state = load_json(STATE_FILE)
    
    if not isinstance(state, dict): state = {}
    
    # 2. Identificar perfis pendentes (priorizando os que nunca foram ou foram há mais tempo)
    profile_list = []
    for p in profiles:
        username = p["username"]
        last_scraped = state.get(username, "2000-01-01T00:00:00")
        profile_list.append({
            "username": username,
            "last_scraped": datetime.fromisoformat(last_scraped)
        })
    
    # Ordenar por data da última coleta (mais antigos primeiro)
    profile_list.sort(key=lambda x: x["last_scraped"])
    
    # Selecionar o próximo lote
    targets = profile_list[:PROFILES_PER_RUN]
    target_usernames = [t["username"] for t in targets]
    
    print(f"📈 Lote selecionado ({len(target_usernames)} perfis): {', '.join(target_usernames)}")
    
    # 3. Executar Raspagem
    scraper = ApifyFullScraper()
    # Mockando a lista de perfis apenas com os alvos do turno para o scraper
    original_profiles_file = scraper.profiles_file
    temp_profiles_path = "data/temp_targets.json"
    
    temp_targets = [{"username": u} for u in target_usernames]
    save_json(temp_profiles_path, temp_targets)
    
    scraper.profiles_file = temp_profiles_path
    
    try:
        stats = scraper.run_full_scrape(
            posts_per_profile=POSTS_PER_PROFILE, 
            comments_per_post=COMMENTS_PER_POST
        )
        
        # 4. Atualizar Estado apenas para sucessos (ou tentativa realizada)
        now_iso = datetime.now().isoformat()
        for username in target_usernames:
            state[username] = now_iso
            
        save_json(STATE_FILE, state)
        print(f"✅ Estado de coleta atualizado para {len(target_usernames)} perfis.")
        
    except Exception as e:
        print(f"❌ Erro crítico na rodada: {e}")
    finally:
        if os.path.exists(temp_profiles_path):
            os.remove(temp_profiles_path)

if __name__ == "__main__":
    run_orchestrated_collection()
