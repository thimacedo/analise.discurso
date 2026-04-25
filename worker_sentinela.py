import os
import time
import json
import httpx
from datetime import datetime, timedelta

# Configurações do Ambiente
env_path = ".env"
config = {}
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                config[k.strip()] = v.strip().strip('"').strip("'")

def get_env(key, default=None):
    return os.environ.get(key) or config.get(key, default)

SUPABASE_URL = get_env("SUPABASE_URL")
SUPABASE_KEY = get_env("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def log_worker(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def get_queue():
    # Busca candidatos ordenados por data de última análise (os mais antigos primeiro)
    # E prioritários (podemos usar uma coluna 'is_priority' se existir, ou gap > 24h)
    r = httpx.get(f"{SUPABASE_URL}/rest/v1/candidatos?select=id,username,data_ultima_analise,is_priority&order=data_ultima_analise.asc.nullsfirst", headers=headers)
    return r.json()

def run_scrape_batch(profiles):
    if not profiles: return
    
    # Criar um arquivo temporário de fila para o raspar.py ler
    with open("temp_queue.json", "w") as f:
        json.dump(profiles, f)
        
    log_worker(f"Iniciando raspagem de {len(profiles)} perfis...")
    # Aqui chamamos o motor principal de raspagem
    # Assumindo que raspar.py pode receber uma lista de perfis
    os.system(f"python raspar.py --file temp_queue.json")

def main():
    log_worker("Iniciando Ciclo Diário de Monitoramento Sentinela...")
    
    all_candidates = get_queue()
    
    # Separar prioritários (Ex: Gap > 24h ou flag manual)
    prioritarios = [c for c in all_candidates if c.get('is_priority') or not c.get('data_ultima_analise')]
    sequenciais = [c for c in all_candidates if c not in prioritarios]
    
    # 1. Processar 100% dos prioritários
    log_worker(f"Prioritários identificados: {len(prioritarios)}")
    run_scrape_batch(prioritarios)
    
    # 2. Processar sequenciais dentro da margem de segurança (Ex: Max 30 por dia para evitar block)
    margem_seguranca = 30
    a_processar = sequenciais[:margem_seguranca]
    
    log_worker(f"Processando sequenciais (Margem Segura): {len(a_processar)}")
    run_scrape_batch(a_processar)
    
    log_worker("Ciclo concluído com sucesso.")

if __name__ == "__main__":
    main()
