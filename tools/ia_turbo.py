import os
import sys
import time
import httpx
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para importar core
sys.path.append(os.getcwd())

from core.qwen_classifier import run_integrated_qwen_classification

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

def get_pending_count():
    try:
        url = f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=not.eq.true"
        resp = httpx.get(url, headers=HEADERS, params={'select': 'count'})
        data = resp.json()
        return data[0]['count'] if data else 0
    except Exception as e:
        print(f"Erro ao contar pendentes: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 IA TURBO: Processando fila de comentários (Sem Scraper)...")
    
    while True:
        pending = get_pending_count()
        print(f"\n📊 Saldo Pendente: {pending} comentários.")
        
        if pending <= 0:
            print("✨ Fila de IA zerada com sucesso!")
            break
            
        print("⚡ Iniciando processamento de lote...")
        try:
            run_integrated_qwen_classification()
        except Exception as e:
            print(f"⚠️ Erro no ciclo de IA: {e}")
        
        # Pausa curta para evitar sobrecarga local
        time.sleep(1)

    print("\n✅ OPERAÇÃO IA CONCLUÍDA.")
