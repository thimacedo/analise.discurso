"""
PASA v49 - Watchdog: Guardião Inteligente com Anti-Spam e Diagnóstico
Diferencia erros de código (falha de import) de erros de runtime (API caiu).
Nunca spama o operador em loop por causa de erro de desenvolvedor.
"""
import time
import subprocess
import sys
import os
import requests
from typing import Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.auto_updater import check_for_updates
    from core.zyte_checker import check_zyte_health, check_scrapy_cloud_health
except ImportError:
    check_for_updates = lambda: False
    check_zyte_health = lambda: (True, "Skipped")
    check_scrapy_cloud_health = lambda: (True, "Skipped")

# --- Configurações ---
SERVER_SCRIPT = "local_server.py"
RESTART_DELAY = 30
ZYTE_CHECK_INTERVAL = 1800  # 30 minutos
REQUIREMENTS_FILE = "requirements.txt"

CACHE_DIR = r"E:\sentinela_temp\pip_cache"
TEMP_DIR = r"E:\sentinela_temp\tmp"

CHILD_ENV = os.environ.copy()
CHILD_ENV["PIP_CACHE_DIR"] = CACHE_DIR
CHILD_ENV["TMP"] = TEMP_DIR
CHILD_ENV["TEMP"] = TEMP_DIR

CALLMEBOT_PHONE = "558496066876"
CALLMEBOT_APIKEY = "8552672"
CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"

# Erros que indicam problema de código (não adianta reiniciar)
CODE_ERRORS = [
    "importerror",
    "modulenotfounderror",
    "syntaxerror",
    "indentationerror",
    "attributeerror",
    "nameerror",
    "typeerror",
]

# Estado global de alertas
last_alert_time = 0
ALERT_COOLDOWN = 600  # 10 minutos entre alertas


def get_python_executable() -> str:
    """Detecta o executável Python do ambiente virtual (venv ou .venv)."""
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


def classify_error(stderr_output: str) -> str:
    """Classifica o erro como 'code' (desenvolvedor) ou 'runtime' (sistema)."""
    if not stderr_output:
        return "runtime"
    stderr_lower = stderr_output.lower()
    for err_type in CODE_ERRORS:
        if err_type in stderr_lower:
            return "code"
    return "runtime"


def heal_dependencies(python_exe: str) -> None:
    """Verifica e instala dependências, com estratégia de auto-cura do cache."""
    print("[Watchdog] Verificando integridade das dependências...")
    try:
        subprocess.run(
            [python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE, "-q"],
            check=True,
            env=CHILD_ENV,
        )
        print("[Watchdog] Dependências sincronizadas.")
    except subprocess.CalledProcessError:
        print("[Watchdog] Falha na instalação. Purgando cache...")
        try:
            subprocess.run(
                [python_exe, "-m", "pip", "cache", "purge"],
                check=True,
                env=CHILD_ENV,
            )
            subprocess.run(
                [python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE, "-q"],
                check=True,
                env=CHILD_ENV,
            )
            print("[Watchdog] Dependências sincronizadas após purga de cache.")
        except Exception as e2:
            print(f"[Watchdog] Falha crítica ao curar dependências: {e2}")


def send_whatsapp_alert(message: str) -> None:
    """Dispara alerta via WhatsApp usando CallMeBot, com cooldown anti-spam."""
    global last_alert_time
    now = time.time()
    if now - last_alert_time < ALERT_COOLDOWN:
        print("[Watchdog] Alerta suprimido (cooldown ativo).")
        return

    try:
        params = {
            "phone": CALLMEBOT_PHONE,
            "apikey": CALLMEBOT_APIKEY,
            "text": message,
        }
        requests.get(CALLMEBOT_URL, params=params, timeout=10)
        last_alert_time = now
        print("[Watchdog] Alerta WhatsApp enviado.")
    except Exception as e:
        print(f"[Watchdog] Falha ao enviar alerta: {e}")


def check_api_health() -> None:
    """Verifica a saúde das APIs Zyte e toma ações preventivas."""
    print("[Watchdog] Executando check-up periódico das APIs Zyte...")

    # Check 1: Zyte Extraction API
    zyte_ok, zyte_msg = check_zyte_health()
    if not zyte_ok:
        send_whatsapp_alert(
            f"🚩 *ZYTE EXTRACTION ALERT* 🚩\nMotivo: `{zyte_msg}`"
        )
        os.environ["ZYTE_DISABLED"] = "true"
        print("[Watchdog] Motor Zyte PAUSADO devido a falha crítica.")
    else:
        if os.getenv("ZYTE_DISABLED") == "true":
            os.environ["ZYTE_DISABLED"] = "false"
            print("[Watchdog] Motor Zyte RECUPERADO. Retomando uso.")

    # Check 2: Scrapy Cloud (apenas alerta, não pausa nada)
    scrapy_ok, scrapy_msg = check_scrapy_cloud_health()
    if not scrapy_ok and os.getenv("SCRAPY_CLOUD_API_KEY"):
        send_whatsapp_alert(
            f"⚠️ *SCRAPY CLOUD ALERT* ⚠️\nMotivo: `{scrapy_msg}`"
        )


def handle_process_failure(
    poll: int, stderr_output: str, consecutive_code_errors: int
) -> Tuple[bool, int]:
    """
    Trata a falha do processo filho.
    Retorna (deve_parar: bool, consecutive_code_errors: int).
    """
    error_type = classify_error(stderr_output)

    if error_type == "code":
        consecutive_code_errors += 1
        print(f"[Watchdog] ⛔ ERRO DE CÓDIGO detectado (tentativa {consecutive_code_errors})")
        print(f"[Watchdog] Detalhes: {stderr_output[:200]}")

        if consecutive_code_errors >= 3:
            send_whatsapp_alert(
                f"🛑 *WATCHDOG: ERRO DE CÓDIGO* 🛑\n"
                f"Servidor falhou {consecutive_code_errors}x seguidas.\n"
                "Reinícios parados. Correção manual necessária.\n"
                f"Erro: `{stderr_output[:100]}`"
            )
            print("[Watchdog] 🛑 3 erros de código consecutivos. Parando reinícios automáticos.")
            return True, consecutive_code_errors
        else:
            if consecutive_code_errors == 1:
                heal_dependencies(get_python_executable())
    else:
        consecutive_code_errors = 0
        print("[Watchdog] ⚠️ Erro de runtime detectado. Reiniciando...")
        send_whatsapp_alert(
            f"🚨 *WATCHDOG: RUNTIME ERROR* 🚨\n"
            f"Servidor travou (Code: {poll}).\n"
            "Reinício automático em andamento."
        )

    return False, consecutive_code_errors


def guard() -> None:
    """Loop principal do guardião. Monitora, diagnostica e reinicia o servidor."""
    python_exe = get_python_executable()
    last_zyte_check = 0
    consecutive_code_errors = 0

    while True:
        # Verificação de Saúde das APIs Zyte
        if time.time() - last_zyte_check > ZYTE_CHECK_INTERVAL:
            check_api_health()
            last_zyte_check = time.time()

        # Verificação de atualizações
        try:
            if check_for_updates():
                heal_dependencies(python_exe)
        except Exception:
            pass

        # Inicialização e monitoramento do processo filho
        try:
            process = subprocess.Popen(
                [python_exe, SERVER_SCRIPT],
                env=CHILD_ENV,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            while True:
                poll = process.poll()
                if poll is not None:
                    break
                time.sleep(10)

            if poll != 0:
                stderr_output = process.stderr.read() if process.stderr else ""
                should_stop, consecutive_code_errors = handle_process_failure(
                    poll, stderr_output, consecutive_code_errors
                )
                if should_stop:
                    break
            else:
                consecutive_code_errors = 0

        except KeyboardInterrupt:
            print("\n[Watchdog] Interrompido pelo operador.")
            break
        except Exception as e:
            print(f"[Watchdog] Exceção no guardião: {e}")

        # Delay adaptativo: mais tempo se o erro é repetitivo
        delay = RESTART_DELAY * min(consecutive_code_errors + 1, 5)
        time.sleep(delay)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("=" * 50)
    print("🛡️ SENTINELA DEMOCRÁTICA - WATCHDOG v49.9")
    print("=" * 50)
    guard()
