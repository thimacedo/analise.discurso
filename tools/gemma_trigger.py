import subprocess
import sys
import os
import httpx
import json
import time
from datetime import datetime

def query_gemma_decision(state_context):
    endpoint = "http://localhost:11434/v1/chat/completions"
    prompt = f"""
    ESTADO ATUAL: {state_context}
    DATA ATUAL: {datetime.now().isoformat()}
    
    Analise os perfis acima. Se o tempo desde a última raspagem for > 12 horas, precisamos de dados novos.
    Se a carga do sistema estiver baixa, podemos raspar.
    Responda apenas YES ou NO se devemos raspar agora.
    """
    payload = {"model": "gemma:2b", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
    try:
        response = httpx.post(endpoint, json=payload, timeout=60.0)
        return "YES" in response.json()['choices'][0]['message']['content'].strip().upper()
    except Exception as e:
        print(f"⚠️ Gemma falhou, modo resiliência (fail-open): {e}")
        return True

def run_orchestrator():
    print("🌙 [GEMMA-ORCHESTRATOR] Operação Noturna Iniciada...")
    while True:
        with open("data/collection_state.json", "r") as f:
            state = f.read()
        
        if query_gemma_decision(state):
            print(f"🚀 [{datetime.now()}] Gemma autorizou: Iniciando ciclo de povoamento (Centralizado)...")
            subprocess.run([sys.executable, "-m", "core.orquestrador"], check=False)
        else:
            print(f"💤 [{datetime.now()}] Gemma descansando: Sem necessidade de raspagem no momento.")
            
        time.sleep(3600) # Dorme 1 hora entre avaliações

if __name__ == "__main__":
    run_orchestrator()
