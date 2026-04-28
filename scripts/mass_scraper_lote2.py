import os
import requests
import json
import time

# Configurações
APIFY_TOKEN = os.environ.get("SENTINELA_APIFY_API_TOKEN")
SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "SUPABASE_KEY_PLACEHOLDER")

# Lista de Governadores e Deputados (Lote 2)
USERNAMES = [
    "tarcisiogdf", "romeuzemaoficial", "helderbarbalho", "eduardoleite45", 
    "raquellyraoficial", "fatimabezerra13", "jeronimorodriguesba", "claudio_castro", 
    "ratinho_junior", "mauromendesoficial", "carla.zambelli", "guilherme_boulos", 
    "tabataamaralsp", "kimkataguiri", "gleisihoffmann", "janoneresreal", 
    "eduardobolsonaro", "flaviobolsonaro", "marcelovanhattem"
]

def run_mass_scrape():
    print(f"🐝 Disparando Apify Scraper para {len(USERNAMES)} perfis...")
    
    # URL do Actor instagram-scraper
    run_url = f"https://api.apify.com/v2/acts/apify~instagram-scraper/runs?token={APIFY_TOKEN}"
    
    payload = {
        "addParentData": True,
        "directUrls": [f"https://www.instagram.com/{u}/" for u in USERNAMES],
        "resultsLimit": 10,
        "resultsType": "posts",
        "searchLimit": 1
    }
    
    try:
        response = requests.post(run_url, json=payload)
        if response.status_code == 201:
            run_data = response.json()
            run_id = run_data['data']['id']
            dataset_id = run_data['data']['defaultDatasetId']
            print(f"🚀 Execução iniciada! Run ID: {run_id}")
            print(f"📊 Dataset ID: {dataset_id}")
            
            # Registrar no log local para recuperação posterior
            with open("data/last_scrape_info.json", "w") as f:
                json.dump({"run_id": run_id, "dataset_id": dataset_id, "timestamp": time.time()}, f)
            
            return run_id, dataset_id
        else:
            print(f"❌ Erro ao iniciar: {response.text}")
    except Exception as e:
        print(f"❌ Falha crítica: {e}")
    return None, None

if __name__ == "__main__":
    run_mass_scrape()
