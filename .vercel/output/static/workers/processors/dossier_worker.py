
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import time
import os
import logging
from datetime import datetime
from supabase import create_client, Client
import pandas as pd
from processing.report_generator import ReportGenerator

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração via env
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        logging.error("Variáveis SUPABASE_URL ou SUPABASE_KEY não configuradas.")
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logging.error(f"Erro ao conectar ao Supabase: {e}")
        return None

supabase = get_supabase_client()

# Ensure reports directory exists
REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

def process_queue():
    if not supabase:
        logging.error("Supabase offline. Abortando.")
        return

    try:
        # Buscar pendentes
        res = supabase.table('dossies').select('*').eq('status', 'Pendente').execute()
        
        if not res.data:
            logging.info("Nada na fila.")
            return

        logging.info(f"Processando {len(res.data)} dossiês.")
        
        for dossier in res.data:
            d_id = dossier.get('id')
            logging.info(f"-> Inicidando ID {d_id}")

            try:
                # Marcar como Processando
                supabase.table('dossies').update({'status': 'Processando'}).eq('id', d_id).execute()
                
                # Dados
                df = pd.DataFrame([dossier])
                candidato_id = dossier.get('candidato_id', f'd_{d_id}')
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # Nome seguro
                safe_name = "".join(c for c in str(candidato_id) if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_')
                pdf_name = f"{safe_name}_{ts}.pdf"
                out_path = os.path.join(REPORT_DIR, pdf_name)
                
                # Gerar
                generator = ReportGenerator()
                gen_path = generator.generate_pdf(df, out_path)

                if gen_path and os.path.exists(gen_path):
                    supabase.table('dossies').update({
                        'status': 'Concluído', 
                        'report_path': gen_path
                    }).eq('id', d_id).execute()
                    logging.info(f"✅ Sucesso: {d_id}")
                else:
                    raise Exception("Gerador de PDF falhou.")

            except Exception as e:
                logging.error(f"❌ Erro no dossiê {d_id}: {e}")
                supabase.table('dossies').update({
                    'status': 'Falhou', 
                    'error_log': str(e)
                }).eq('id', d_id).execute()

    except Exception as e:
        logging.error(f"Erro no loop: {e}")

if __name__ == '__main__':
    logging.info("🚀 DossierWorker Iniciado.")
    while True:
        process_queue()
        time.sleep(10)

