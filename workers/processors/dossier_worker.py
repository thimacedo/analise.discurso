import time
import os
import logging
from supabase import create_client, Client
import pandas as pd
from processing.report_generator import ReportGenerator # Assuming this path is correct

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Supabase connection details (should ideally come from env vars or config)
# Assuming SUPABASE_URL and SUPABASE_KEY are set in the environment
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logging.info("Conexão com Supabase estabelecida.")
    except Exception as e:
        logging.error(f"Falha ao conectar ao Supabase: {e}")
else:
    logging.error("Variáveis de ambiente SUPABASE_URL ou SUPABASE_KEY não encontradas.")

# Ensure reports directory exists
REPORT_DIR = "reports"
if not os.path.exists(REPORT_DIR):
    try:
        os.makedirs(REPORT_DIR)
        logging.info(f"Diretório '{REPORT_DIR}' criado.")
    except OSError as e:
        logging.error(f"Falha ao criar o diretório '{REPORT_DIR}': {e}")
        # If reports directory cannot be created, subsequent operations might fail.

def process_queue():
    """
    Conecta ao Supabase, busca dossiês pendentes, gera PDFs e atualiza seus status.
    """
    if not supabase:
        logging.error("Cliente Supabase não inicializado. Não é possível processar a fila.")
        return

    logging.info("Aguardando dossiês...")
    try:
        # Buscar registros pendentes
        # O método .execute() pode retornar um erro em .response.status_code
        response = supabase.from_('dossies').select('*').eq('status', 'Pendente').execute()

        # Verificar se a resposta contém dados e se não há erros na requisição
        if response.data is not None and response.count is not None and response.count > 0:
            logging.info(f"Encontrados {response.count} dossiês pendentes.")
            
            for dossier in response.data:
                dossier_id = dossier.get('id')
                if not dossier_id:
                    logging.warning("Dossiê sem ID encontrado, pulando.")
                    continue

                logging.info(f"Processando dossiê ID: {dossier_id}")

                # Atualizar status para 'Processando'
                try:
                    update_response_processing = supabase.from_('dossies').update({'status': 'Processando'}).eq('id', dossier_id).execute()
                    # Verificar se a operação não retornou um erro explícito.
                    if update_response_processing.error is not None:
                         raise Exception(f"Supabase error: {update_response_processing.error}")
                    logging.info(f"Status do dossiê {dossier_id} atualizado para 'Processando'.")
                except Exception as e:
                    logging.error(f"Falha ao atualizar status para 'Processando' no dossiê ID: {dossier_id}. Erro: {e}")
                    # Se não conseguir marcar como 'Processando', pular para o próximo.
                    continue
                
                try:
                    # Preparar dados para geração do PDF
                    # Criar um DataFrame a partir do dicionário do dossiê
                    df_dossier = pd.DataFrame([dossier])
                    
                    # Definir nome do arquivo PDF
                    # Usar candidato_id se disponível, senão usar ID do dossiê
                    candidato_id = dossier.get('candidato_id', f'dossier_{dossier_id}')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    # Sanitizar candidato_id para uso em nome de arquivo
                    sanitized_candidato_id = "".join(c for c in candidato_id if c.isalnum() or c in (' ', '_')).rstrip()
                    pdf_filename = f"{sanitized_candidato_id.replace(' ', '_')}_{timestamp}.pdf" 
                    output_path = os.path.join(REPORT_DIR, pdf_filename)
                    
                    # Gerar PDF
                    generator = ReportGenerator()
                    generated_path = generator.generate_pdf(df_dossier, output_path)

                    if generated_path and os.path.exists(generated_path):
                        # Atualizar status para 'Concluído' e salvar caminho do relatório
                        update_response_completed = supabase.from_('dossies').update({'status': 'Concluído', 'report_path': generated_path}).eq('id', dossier_id).execute()
                        if update_response_completed.error is not None:
                            raise Exception(f"Supabase error: {update_response_completed.error}")
                        logging.info(f"Dossiê ID: {dossier_id} concluído. PDF salvo em: {generated_path}")
                    else:
                        # Se a geração do PDF falhou ou o caminho não foi retornado/encontrado
                        raise ValueError("Geração do PDF falhou ou caminho de saída inválido/não encontrado.")

                except Exception as e:
                    logging.error(f"Erro ao processar dossiê ID {dossier_id}: {e}")
                    # Atualizar status para 'Falhou' e logar o erro
                    try:
                        supabase.from_('dossies').update({'status': 'Falhou', 'error_log': str(e)}).eq('id', dossier_id).execute()
                    except Exception as db_err:
                        logging.error(f"Erro ao atualizar status para 'Falhou' para dossiê ID {dossier_id}: {db_err}")
                        
        else:
            logging.info("Nenhum dossiê pendente encontrado.")

    except Exception as e:
        logging.error(f"Erro geral no loop de processamento: {e}")

if __name__ == '__main__':
    logging.info("Inicializando Worker de Dossiês...")
    # Ensure Supabase client is ready before entering the loop
    if not supabase:
        logging.error("Cliente Supabase não inicializado. Worker não será iniciado.")
    else:
        while True:
            try:
                process_queue()
            except Exception as loop_e:
                logging.error(f"Exceção inesperada no loop principal: {loop_e}. Reiniciando em 60s.")
                time.sleep(60) # Wait longer after an unexpected loop error
            time.sleep(10)
