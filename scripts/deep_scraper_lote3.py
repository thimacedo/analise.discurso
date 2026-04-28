import os
import json
import requests
import time

# Configurações
APIFY_TOKEN = os.environ.get("SENTINELA_APIFY_API_TOKEN")
GAP_REPORT_PATH = "data/gap_analysis_report.json"

def run_deep_scrape():
    if not os.path.exists(GAP_REPORT_PATH):
        print("❌ Erro: Relatório de gaps não encontrado.")
        return

    with open(GAP_REPORT_PATH, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    # Filtrar monitorados sem dados (Lote 3)
    # in_db: false -> Perfil novo não sincronizado
    # posts: 0 -> Perfil no DB mas sem histórico capturado
    targets = [p['username'] for p in profiles if not p['in_db'] or (p.get('posts') or 0) == 0]
    
    if not targets:
        print("✅ Todos os monitorados já possuem dados. Iniciando atualização de rotina...")
        targets = [p['username'] for p in profiles[:10]] # Amostra de rotina
    
    print(f"🐝 Iniciando Deep Scrape para {len(targets)} perfis críticos...")
    print(f"📋 Alvos prioritários: {', '.join(targets[:10])}...")

    # Dividir em lotes de 40 para respeitar limites do Apify por execução
    batch_size = 40
    for i in range(0, len(targets), batch_size):
        batch = targets[i:i+batch_size]
        print(f"🚀 Disparando Lote {i//batch_size + 1} ({len(batch)} perfis)...")
        
        run_url = f"https://api.apify.com/v2/acts/apify~instagram-scraper/runs?token={APIFY_TOKEN}"
        
        payload = {
            "addParentData": True,
            "directUrls": [f"https://www.instagram.com/{u}/" for u in batch],
            "resultsLimit": 15, # 15 posts (Equilíbrio entre custo e amostragem estatística)
            "resultsType": "posts",
            "searchLimit": 1
        }
        
        try:
            res = requests.post(run_url, json=payload)
            if res.status_code == 201:
                run_id = res.json()['data']['id']
                print(f" ✅ Lote {i//batch_size + 1} ONLINE. Run ID: {run_id}")
            else:
                print(f" ❌ Erro no lote: {res.text}")
        except Exception as e:
            print(f" ❌ Falha na conexão: {e}")
        
        # Pequeno delay entre disparos de lotes
        time.sleep(2)

if __name__ == "__main__":
    run_deep_scrape()
