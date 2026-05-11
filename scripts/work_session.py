import os, sys, time, subprocess
from datetime import datetime

# Ensure the project root is in the Python path
# This is crucial for importing modules from other directories like 'core' and 'tools'.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

log_path = os.path.join(project_root, "logs", "worker.log")

def log_msg(msg):
    """Logs a message to both the console and the worker.log file with a timestamp."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {msg}
"
    
    # Print to console
    print(line, end="")
    
    # Append to log file
    try:
        # Ensure the log directory exists
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line)
    except Exception as e:
        # Log file writing errors to stderr to not obscure stdout
        print(f"Error writing to log file {log_path}: {e}", file=sys.stderr)

def run_command_and_log(command: str, script_name: str):
    """
    Executes a command and streams its stdout and stderr to both the console and the log file.
    Uses shell=True as specified by the user's example command.
    """
    log_msg(f"--- Iniciando {script_name} ---")
    try:
        # Construct the full command to be executed by the shell
        # Ensure PYTHONPATH is set for subprocess if needed, especially for internal module imports.
        env = os.environ.copy()
        # Setting PYTHONPATH to include the project root explicitly for the subprocess.
        # sys.path[-1] is likely the project root if added earlier.
        # If not, explicitly use project_root.
        env["PYTHONPATH"] = project_root # Ensure project root is in PYTHONPATH for subprocess
        
        # Use Popen for streaming output
        proc = subprocess.Popen(
            command, 
            shell=True, 
            env=env,
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, # Redirect stderr to stdout
            text=True, # Decode output as text
            cwd=project_root # Set working directory to project root
        )

        # Stream output line by line
        for output_line in proc.stdout:
            # Print to console
            print(output_line, end="")
            # Write to log file
            try:
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(output_line)
            except Exception as e:
                print(f"Error writing to log file {log_path}: {e}", file=sys.stderr)
        
        # Wait for the process to complete and check return code
        proc.wait()
        if proc.returncode != 0:
            log_msg(f"!!! {script_name} finalizado com erro (código {proc.returncode}) !!!")
        else:
            log_msg(f"--- {script_name} concluído com sucesso ---")
            
    except FileNotFoundError:
        log_msg(f"!!! Erro: Comando '{command}' não encontrado. Verifique o caminho e as permissões. !!!")
    except Exception as e:
        log_msg(f"!!! Erro inesperado ao executar '{command}': {e} !!!")

def run_routine():
    """Executa a sequência de tarefas da rotina diária."""
    scripts_to_run = [
        ("Limpeza", "python tools/cleanup_ghosts.py"),
        ("Raspagem", "python core/orquestrador.py"),
        ("IA / Classificação", "python tools/process_backlog.py"),
        ("Dashboards / KPIs", "python scripts/update_kpis.py")
    ]
    
    for name, cmd in scripts_to_run:
        run_command_and_log(cmd, name)

if __name__ == "__main__":
    log_msg("🛡️ MODO WORK SESSION ATIVADO. Pressione Ctrl+C para parar.")
    try:
        while True:
            run_routine()
            sleep_duration = 1800  # 30 minutos
            log_msg(f"⏳ Ciclo concluído. Dormindo por {sleep_duration // 60} minutos...")
            time.sleep(sleep_duration)
    except KeyboardInterrupt:
        log_msg("🛑 Work Session encerrada manualmente. Bom descanso!")
        sys.exit(0)
    except Exception as e:
        log_msg(f"!!! Erro inesperado no loop principal: {e}. Reiniciando em 60 segundos. !!!")
        time.sleep(60)
