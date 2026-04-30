import subprocess
import os
import sys
import time
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

def get_pending_count():
    try:
        url = f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.false"
        resp = httpx.get(url, headers=HEADERS, params={'select': 'count'})
        data = resp.json()
        return data[0]['count'] if data else 0
    except Exception as e:
        print(f"Erro ao contar pendentes: {e}")
        return 0

def run_orchestrator():
    print("\n🔄 Iniciando ciclo do orquestrador...")
    process = subprocess.run([sys.executable, "orquestrador.py"], capture_output=False, text=True)
    return process.returncode

if __name__ == "__main__":
    print("🚀 MODO TURBO: Zerando a fila de processamento IA...")
    
    while True:
        pending = get_pending_count()
        print(f"\n📊 Saldo Pendente: {pending} comentários.")
        
        if pending <= 0:
            print("✨ Fila zerada com sucesso!")
            break
            
        print("⚡ Executando ciclo incremental (Batch 100)...")
        run_orchestrator()
        
        # Pequena pausa para respiro do sistema
        time.sleep(2)

    print("\n✅ OPERAÇÃO CONCLUÍDA.")
