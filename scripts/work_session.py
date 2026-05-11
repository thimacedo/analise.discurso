import os
import sys
import time
import subprocess
import logging
from datetime import datetime

# --- Custom Stream Handler for Logging and Console Output ---
class DualStreamHandler:
    def __init__(self, filename, mode='a', encoding='utf-8'):
        self.terminal = sys.stdout # Keep reference to original stdout if needed, or just use it directly
        self.log_file = open(filename, mode, encoding=encoding)

    def write(self, message):
        # Get current timestamp for log file
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"{timestamp} - {message.strip()}"
        
        # Write to console using the original stdout reference
        print(message, end='', file=self.terminal)
        
        # Write to log file
        self.log_file.write(formatted_message + '
')
        self.log_file.flush()

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        self.log_file.close()

# --- Configuration ---
LOG_FILE_PATH = 'logs/worker.log'
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__) + '/..')

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

# --- Setup Redirection ---
# Create and install the dual stream handler
dual_handler = DualStreamHandler(LOG_FILE_PATH)

# Store original stdout/stderr
original_stdout = sys.stdout
original_stderr = sys.stderr

# Redirect sys.stdout and sys.stderr
sys.stdout = dual_handler
sys.stderr = dual_handler

# Configure logging
root_logger = logging.getLogger()
if root_logger.hasHandlers():
    root_logger.handlers.clear()

root_logger.setLevel(logging.INFO)
# Create a handler that writes to our dual_handler stream
log_stream_handler = logging.StreamHandler(dual_handler) 
log_stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
root_logger.addHandler(log_stream_handler)


# --- Original script content ---

# Add project root to PYTHONPATH for module imports
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# --- Functions ---
def run_command(command: list[str], description: str, env_vars: dict = None):
    """Executa um comando de script Python e exibe logs."""
    logging.info(f"Iniciando: {description}")
    try:
        current_env = os.environ.copy()
        if env_vars:
            current_env.update(env_vars)
        
        python_path = current_env.get('PYTHONPATH', '')
        if PROJECT_ROOT not in python_path.split(os.pathsep):
            current_env['PYTHONPATH'] = f"{PROJECT_ROOT}{os.pathsep}{python_path}".strip(os.pathsep)
        
        # Use sys.executable to ensure the same Python interpreter is used
        process = subprocess.Popen([sys.executable, *command], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True,
                                   cwd=PROJECT_ROOT,
                                   env=current_env)
        
        stdout_lines = []
        stderr_lines = []

        # Read from subprocess pipes and write to our dual handler
        while True:
            stdout_line = process.stdout.readline()
            stderr_line = process.stderr.readline()

            if stdout_line:
                # Use print with end='' to prevent extra newlines, DualStreamHandler adds its own.
                # The DualStreamHandler will write this to the console and the log file.
                print(f"[SUBPROCESS STDOUT] {stdout_line.strip()}", end='
') 
                stdout_lines.append(stdout_line)
            if stderr_line:
                print(f"[SUBPROCESS STDERR] {stderr_line.strip()}", end='
')
                stderr_lines.append(stderr_line)

            # Check if process has finished
            if stdout_line == '' and stderr_line == '' and process.poll() is not None:
                break

        return_code = process.returncode
        if return_code == 0:
            logging.info(f"Sucesso: {description} concluído.")
            return True, "".join(stdout_lines)
        else:
            logging.error(f"Falha: {description} retornou com código {return_code}.")
            # Log the full error from subprocess stderr
            logging.error(f"Erro do subprocesso: {''.join(stderr_lines)}")
            return False, "".join(stderr_lines)
            
    except FileNotFoundError:
        logging.error(f"Erro: Comando '{command[0]}' não encontrado. Verifique se o script existe e está no PATH.")
        return False, "Comando não encontrado."
    except Exception as e:
        logging.error(f"Erro inesperado ao executar '{description}': {e}")
        return False, str(e)

# Placeholder functions (original ones)
def cleanup_timeline():
    return run_command(["tools/cleanup_ghosts.py"], "Limpeza da timeline")

def scraping_targets():
    return run_command(["core/orquestrador.py"], "Raspagem de todos os alvos")

def classify_comments():
    return run_command(["tools/process_backlog.py"], "Classificação das pendências de comentários")

def update_kpis():
    return run_command(["scripts/update_kpis.py"], "Atualização dos KPIs")

# --- Main Routine ---
def run_routine():
    """Executa a sequência de tarefas da rotina diária."""
    tasks = [
        ("Limpeza", cleanup_timeline),
        ("Raspagem", scraping_targets),
        ("IA / Classificação", classify_comments),
        ("Dashboards / KPIs", update_kpis)
    ]
    
    all_tasks_successful = True
    for description, func in tasks:
        success, _ = func()
        if not success:
            all_tasks_successful = False
            logging.warning(f"A tarefa '{description}' falhou. Prosseguindo com as próximas.")
    
    if all_tasks_successful:
        logging.info("Ciclo de trabalho diário concluído com sucesso.")
    else:
        logging.warning("Ciclo de trabalho diário concluído com falhas em algumas tarefas.")

if __name__ == "__main__":
    # Use the original_stdout for the initial message to ensure it appears on the console
    # even if sys.stdout is already reassigned by the time this runs.
    print("🛡️ MODO WORK SESSION ATIVADO. Pressione Ctrl+C para parar.", file=original_stdout)
    try:
        while True:
            run_routine()
            sleep_duration = 1800  # 30 minutos
            logging.info(f"Aguardando {sleep_duration} segundos antes do próximo ciclo...")
            time.sleep(sleep_duration)
    except KeyboardInterrupt:
        logging.info("🛑 Work Session interrompida manualmente. Encerrando...")
        # Restore stdout/stderr before exiting to ensure clean exit message
        sys.stdout = original_stdout
        sys.stderr = original_stderr
        print("Work Session encerrada.", file=original_stdout)
        sys.exit(0)
    except Exception as e:
        logging.error(f"Erro inesperado no loop principal: {e}. Reiniciando em 60 segundos.")
        time.sleep(60)
    finally:
        # Ensure the dual handler is closed if it was opened
        if 'dual_handler' in locals() and dual_handler:
            dual_handler.close()
        # Restore stdout/stderr on unexpected exit
        sys.stdout = original_stdout
        sys.stderr = original_stderr
