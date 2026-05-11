import os
import sys
import time
import subprocess
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Adiciona o diretório raiz do projeto ao PYTHONPATH para garantir que os módulos internos sejam encontrados
# Isso é crucial quando os scripts são executados de subdiretórios (como 'tools' ou 'scripts')
project_root = os.path.abspath(os.path.dirname(__file__) + '/..')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Funções de Tarefas ---

def run_command(command: list[str], description: str, env_vars: dict = None):
    """Executa um comando de script Python e exibe logs."""
    logging.info(f"Iniciando: {description}")
    try:
        # Garante que o comando seja executado com o interpretador Python correto
        # e que o diretório de trabalho seja a raiz do projeto.
        # Atualiza o ambiente com PYTHONPATH para incluir o diretório raiz.
        current_env = os.environ.copy()
        if env_vars:
            current_env.update(env_vars)
        
        # Adiciona o diretório raiz ao PYTHONPATH do subprocesso
        python_path = current_env.get('PYTHONPATH', '')
        if project_root not in python_path.split(os.pathsep):
            current_env['PYTHONPATH'] = f"{project_root}{os.pathsep}{python_path}".strip(os.pathsep)
        
        process = subprocess.Popen([sys.executable, *command], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True,
                                   cwd=project_root, # Define o diretório de trabalho como a raiz do projeto
                                   env=current_env)
        
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
    # O orquestrador agora deve ser encontrado devido ao PYTHONPATH configurado
    return run_command(["core/orquestrador.py"], "Raspagem de todos os alvos")

def classify_comments():
    return run_command(["tools/process_backlog.py"], "Classificação das pendências de comentários")

def update_kpis():
    # O update_kpis também deve funcionar agora se o path para core estiver correto
    return run_command(["scripts/update_kpis.py"], "Atualização dos KPIs")

# --- Loop Principal ---

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
    logging.info("🛡️ MODO WORK SESSION ATIVADO. Pressione Ctrl+C para parar.")
    try:
        while True:
            run_routine()
            sleep_duration = 1800  # 30 minutos
            logging.info(f"Aguardando {sleep_duration} segundos antes do próximo ciclo...")
            time.sleep(sleep_duration)
    except KeyboardInterrupt:
        logging.info("🛑 Work Session interrompida manualmente. Encerrando...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Erro inesperado no loop principal: {e}. Reiniciando em 60 segundos.")
        time.sleep(60)
