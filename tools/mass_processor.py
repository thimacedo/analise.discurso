
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, time, subprocess
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
supa = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def get_pending_count():
    try:
        # Busca contagem exata usando select com head
        res = supa.table('comentarios').select('id', count='exact').neq('processado_ia', True).execute()
        return res.count or 0
    except Exception as e:
        print(f"Erro ao contar: {e}")
        return 0

def run_mass_processing():
    print(f"🚀 [MASS PROCESSOR] Iniciando processamento total...")
    
    while True:
        pending = get_pending_count()
        if pending == 0:
            print("✅ [MASS PROCESSOR] Fila zerada. Finalizando.")
            break
            
        print(f"📦 [MASS PROCESSOR] {pending} comentários restantes. Iniciando lote de 100...")
        
        # Executa o script de processamento de backlog
        # Usamos subprocess para garantir isolamento e execução limpa
        try:
            subprocess.run(["python", "tools/process_backlog.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ [MASS PROCESSOR] Erro no lote: {e}. Tentando novamente em 5s...")
            time.sleep(5)
            continue
            
        print(f"⏳ [MASS PROCESSOR] Lote finalizado. Aguardando 2s para o próximo...")
        time.sleep(2)

if __name__ == "__main__":
    run_mass_processing()
