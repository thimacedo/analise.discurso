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
    from core.zyte_checker import check_zyte_health
except ImportError:
    check_for_updates = lambda: False
    check_zyte_health = lambda: (True, "Skipped")

SERVER_SCRIPT = "local_server.py"
RESTART_DELAY = 30
ZYTE_CHECK_INTERVAL = 1800 # 30 min
REQUIREMENTS_FILE = "requirements.txt"

# Configurações de Drive (Resiliência)
CACHE_DIR = r"E:\sentinela_temp\pip_cache"
TEMP_DIR = r"E:\sentinela_temp\tmp"

# Ambiente customizado para processos filhos
CHILD_ENV = os.environ.copy()
CHILD_ENV["PIP_CACHE_DIR"] = CACHE_DIR
CHILD_ENV["TMP"] = TEMP_DIR
CHILD_ENV["TEMP"] = TEMP_DIR

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
    """Verifica e instala dependências, com estratégia de auto-cura do cache em caso de erro."""
    print("[Watchdog] Verificando integridade das dependências...")
    try:
        subprocess.run(
            [python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE, "-q"], 
            check=True, env=CHILD_ENV
        )
        print("[Watchdog] Dependências sincronizadas com sucesso.")
    except Exception as e:
        print(f"[Watchdog] Falha na instalação. Tentando purgar cache do pip para liberar espaço...")
        try:
            subprocess.run([python_exe, "-m", "pip", "cache", "purge"], check=True, env=CHILD_ENV)
            subprocess.run(
                [python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE, "-q"], 
                check=True, env=CHILD_ENV
            )
            print("[Watchdog] Dependências sincronizadas após purga de cache.")
        except Exception as e2:
            print(f"[Watchdog] Falha crítica ao curar dependências: {e2}")

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
    python_exe = get_python_executable()
    last_zyte_check = 0
    
    while True:
        # 0. Verificação de Saúde do Motor Zyte (Silencioso se OK)
        if time.time() - last_zyte_check > ZYTE_CHECK_INTERVAL:
            zyte_ok, zyte_msg = check_zyte_health()
            if not zyte_ok:
                send_whatsapp_alert(f"🚩 *ZYTE API ALERT* 🚩\nMotivo: `{zyte_msg}`")
            last_zyte_check = time.time()

        try:
            if check_for_updates():
                heal_dependencies(python_exe)
        except Exception:
            pass
        
        # Só instala se necessário
        # heal_dependencies(python_exe) # Removido para evitar log desnecessário a cada ciclo

        try:
            process = subprocess.Popen([python_exe, SERVER_SCRIPT], env=CHILD_ENV)
            
            while True:
                poll = process.poll()
                if poll is not None:
                    if poll != 0:
                        send_whatsapp_alert(f"🚨 *WATCHDOG ALERT* 🚨\nServidor travou (Code: {poll})")
                        heal_dependencies(python_exe)
                    break
                
                time.sleep(10)

        except Exception:
            pass

        time.sleep(RESTART_DELAY)

# Exibe orientações iniciais ao operador
def show_orientations():
    try:
        with open("ORIENTACOES_INICIAIS.md", "r", encoding="utf-8") as f:
            print(f.read())
            print()
    except FileNotFoundError:
        pass

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    show_orientations()  # <-- Chamada adicionada
    guard()
