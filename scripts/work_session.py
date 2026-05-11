import time
import subprocess
import sys
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Funções de Tarefas ---

def run_command(command: list[str], description: str):
    """Executa um comando de script Python e exibe logs."""
    logging.info(f"Iniciando: {description}")
    try:
        # Garante que o comando seja executado com o interpretador Python correto
        # e que o diretório de trabalho seja o raiz do projeto.
        process = subprocess.Popen([sys.executable, *command], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True,
                                   cwd=os.path.abspath(os.path.dirname(__file__) + '/..')) # Define o diretório de trabalho como a raiz do projeto
        
        # Log stdout e stderr em tempo real
        stdout_lines = []
        stderr_lines = []

        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()

            if stdout_line:
                print(f"[STDOUT] {stdout_line.strip()}")
                stdout_lines.append(stdout_line)
            if stderr_line:
                print(f"[STDERR] {stderr_line.strip()}")
                stderr_lines.append(stderr_line)

            if stdout_line == '' and stderr_line == '' and process.poll() is not None:
                break

        return_code = process.returncode
        if return_code == 0:
            logging.info(f"Sucesso: {description} concluído.")
            return True, "".join(stdout_lines)
        else:
            logging.error(f"Falha: {description} retornou com código {return_code}.")
            logging.error(f"Erro completo: {''.join(stderr_lines)}")
            return False, "".join(stderr_lines)
            
    except FileNotFoundError:
        logging.error(f"Erro: Comando '{command[0]}' não encontrado. Verifique se o script existe e está no PATH.")
        return False, "Comando não encontrado."
    except Exception as e:
        logging.error(f"Erro inesperado ao executar '{description}': {e}")
        return False, str(e)

def cleanup_timeline():
    return run_command(["tools/cleanup_ghosts.py"], "Limpeza da timeline")

def scraping_targets():
    # Tentativa de executar o orquestrador com path relativo
    return run_command(["core/orquestrador.py"], "Raspagem de todos os alvos")

def classify_comments():
    return run_command(["tools/process_backlog.py"], "Classificação das pendências de comentários")

def update_kpis():
    # Script que causou SyntaxError anteriormente, vamos tentar executar assim mesmo.
    # O erro original era em 'core/instagram_headless.py' importado por 'update_kpis.py'
    return run_command(["scripts/update_kpis.py"], "Atualização dos KPIs")

# --- Loop Principal ---

def main_work_session():
    """Executa a sessão de trabalho diária em loop."""
    logging.info("Iniciando rotina de sessão de trabalho diária...")
    
    while True:
        try:
            # 1. Limpeza
            success_cleanup, _ = cleanup_timeline()
            if not success_cleanup:
                logging.warning("Falha na etapa de limpeza. Prosseguindo para a próxima etapa.")

            # 2. Coleta (Raspagem)
            # A raspagem pode falhar, mas continuamos para não parar a rotina.
            success_scraping, _ = scraping_targets()
            if not success_scraping:
                logging.warning("Falha na etapa de raspagem. Prosseguindo para a próxima etapa.")

            # 3. Inteligência (Classificação)
            success_classification, _ = classify_comments()
            if not success_classification:
                logging.warning("Falha na etapa de classificação. Prosseguindo para a próxima etapa.")
            
            # 4. Dashboard (Atualização de KPIs)
            # Esta etapa falhou anteriormente devido a SyntaxError.
            success_kpis, _ = update_kpis()
            if not success_kpis:
                logging.warning("Falha na etapa de atualização de KPIs. Prosseguindo para a próxima etapa.")

            logging.info("Ciclo de trabalho diário concluído.")
            
            # 5. Pausa
            sleep_duration = 1800  # 30 minutos
            logging.info(f"Aguardando {sleep_duration} segundos antes do próximo ciclo...")
            time.sleep(sleep_duration)

        except KeyboardInterrupt:
            logging.info("Sessão de trabalho interrompida manualmente. Encerrando...")
            sys.exit(0)
        except Exception as e:
            logging.error(f"Erro inesperado no loop principal: {e}. Reiniciando em 60 segundos.")
            time.sleep(60)

if __name__ == "__main__":
    main_work_session()
