"""
PASA v49 - Watchdog: Guardião com Auto-Cura e Alerta WhatsApp
Monitora o local_server.py, reinicia se travar e avisa o operador via CallMeBot.
"""
import time
import subprocess
import sys
import os
import requests

# Garante que o diretório raiz do projeto esteja no Python Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.auto_updater import check_for_updates
except ImportError:
    check_for_updates = lambda: False

SERVER_SCRIPT = "local_server.py"
RESTART_DELAY = 30
REQUIREMENTS_FILE = "requirements.txt"

CALLMEBOT_PHONE = "558496066876"
CALLMEBOT_APIKEY = "8552672"
CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"

def get_python_executable():
    """Detecta o executável Python do ambiente virtual (venv ou .venv) se disponível."""
    if sys.prefix != sys.base_prefix:
        return sys.executable
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    venv_paths = [
        os.path.join(project_root, ".venv", "Scripts", "python.exe"),
        os.path.join(project_root, "venv", "Scripts", "python.exe"),
        os.path.join(project_root, ".venv", "bin", "python"),
        os.path.join(project_root, "venv", "bin", "python"),
    ]
    
    for path in venv_paths:
        if os.path.exists(path):
            return path
            
    return sys.executable

def heal_dependencies(python_exe):
    """Verifica e instala dependências para garantir a integridade do ambiente."""
    print("[Watchdog] Verificando integridade das dependências...")
    try:
        subprocess.run(
            [python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE, "-q"], 
            check=True
        )
        print("[Watchdog] Dependências sincronizadas com sucesso.")
    except Exception as e:
        print(f"[Watchdog] Falha ao curar dependências: {e}")

def send_whatsapp_alert(message: str):
    """Dispara alerta síncrono via WhatsApp usando CallMeBot."""
    try:
        params = {
            "phone": CALLMEBOT_PHONE,
            "apikey": CALLMEBOT_APIKEY,
            "text": message
        }
        requests.get(CALLMEBOT_URL, params=params, timeout=10)
        print(f"[Watchdog] Alerta WhatsApp enviado.")
    except Exception as e:
        print(f"[Watchdog] Falha ao enviar alerta WhatsApp: {e}")

def guard():
    print("🐕 Watchdog Sentinela v49 ativado. Guardando o Nó Local.")
    python_exe = get_python_executable()
    
    while True:
        try:
            if check_for_updates():
                print("[Watchdog] Atualização detectada. Curando dependências...")
                heal_dependencies(python_exe)
        except Exception as e:
            print(f"[Watchdog] Erro ao verificar atualizações: {e}")
        
        heal_dependencies(python_exe)

        print(f"[Watchdog] Iniciando {SERVER_SCRIPT}...")
        try:
            process = subprocess.Popen([python_exe, SERVER_SCRIPT])
            
            while True:
                poll = process.poll()
                if poll is not None:
                    if poll != 0:
                        error_msg = f"🚨 *WATCHDOG ALERT* 🚨\n\nO *Servidor Sentinela* travou!\nCódigo: `{poll}`\n\nReiniciando em {RESTART_DELAY}s."
                        send_whatsapp_alert(error_msg)
                        heal_dependencies(python_exe)
                    break
                
                time.sleep(10)

        except Exception as e:
            print(f"[Watchdog] Erro ao gerenciar subprocesso: {e}")

        time.sleep(RESTART_DELAY)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    guard()
