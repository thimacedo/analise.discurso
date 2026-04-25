import os
import time
import json
import httpx
from datetime import datetime

# Configurações do Ambiente
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def log_worker(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def get_queue():
    try:
        # Busca candidatos ordenados por 'atualizado_em'
        r = httpx.get(f"{SUPABASE_URL}/rest/v1/candidatos?select=id,username,comentarios_totais_count,atualizado_em&order=atualizado_em.asc.nullsfirst", headers=headers)
        if r.status_code != 200:
            log_worker(f"Erro na API Supabase: {r.status_code}")
            return []
        return r.json()
    except Exception as e:
        log_worker(f"Falha de conexão: {str(e)}")
        return []

def run_scrape_batch(profiles):
    if not profiles: return
    with open("temp_queue.json", "w") as f:
        json.dump(profiles, f)
    log_worker(f"Enviando {len(profiles)} perfis para o motor de raspagem...")
    # Chama o motor principal (ajuste para usar o interpretador correto se necessário)
    os.system(f"python raspar.py --file temp_queue.json")

def main():
    log_worker("🚀 Iniciando Coleta Programada Sentinela...")
    all_candidates = get_queue()
    if not all_candidates:
        log_worker("❌ Sem perfis para processar.")
        return

    # Prioridade: Quem tem 0 ou null comentários
    prioritarios = [c for c in all_candidates if (c.get('comentarios_totais_count') or 0) == 0]
    
    if not prioritarios:
        log_worker("✅ Todos os perfis já possuem dados básicos. Processando fila sequencial por 'atualizado_em'...")
        prioritarios = all_candidates[:20] # Pega os 20 mais antigos

    log_worker(f"📍 Total na fila de execução: {len(prioritarios)}")
    
    # Limita o lote extra solicitado
    lote_max = 50
    a_processar = prioritarios[:lote_max]
    
    run_scrape_batch(a_processar)
    log_worker("✅ Ciclo de coleta finalizado.")

if __name__ == "__main__":
    main()
