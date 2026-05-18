"""
PASA v49 - Watchdog: Guardião Inteligente com Dashboard Web Live
Diferencia erros de código de erros de runtime e transmite tudo via SSE.
"""
import time
import subprocess
import sys
import os
import requests
import json
import asyncio
from threading import Thread, Lock
from typing import Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from core.auto_updater import check_for_updates
    from core.zyte_checker import check_zyte_health, check_scrapy_cloud_health
except ImportError:
    check_for_updates = lambda: False
    check_zyte_health = lambda: (True, "Skipped")
    check_scrapy_cloud_health = lambda: (True, "Skipped")

# --- FastAPI Imports ---
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

# --- Configurações ---
SERVER_SCRIPT = "local_server.py"
RESTART_DELAY = 30
ZYTE_CHECK_INTERVAL = 1800
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

CODE_ERRORS = [
    "importerror", "modulenotfounderror", "syntaxerror",
    "indentationerror", "attributeerror", "nameerror", "typeerror",
]

last_alert_time = 0
ALERT_COOLDOWN = 600

# --- Estado Global Compartilhado (Thread-Safe) ---
class WatchdogState:
    def __init__(self):
        self.lock = Lock()
        self.restarts = 0
        self.code_errors = 0
        self.alerts = 0
        self.zyte_ok = True
        self.status = "OPERACIONAL"
        self.logs = [] # Guarda os últimos N logs para enviar aos novos clientes
        self.clients = [] # Filas asyncio para SSE
        
    def add_log(self, level: str, message: str):
        with self.lock:
            log_entry = {"time": time.strftime("%H:%M:%S"), "level": level, "message": message}
            self.logs.append(log_entry)
            if len(self.logs) > 200:
                self.logs.pop(0)
            # Transmite para todos os clientes conectados
            for queue in self.clients:
                try:
                    queue.put_nowait(log_entry)
                except asyncio.QueueFull:
                    pass
                    
    def update_metrics(self, **kwargs):
        with self.lock:
            for k, v in kwargs.items():
                if hasattr(self, k):
                    setattr(self, k, v)

state = WatchdogState()

# =========================================================
# FASTAPI SERVER (Roda em Thread Separada)
# =========================================================
app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Dashboard não encontrado em /static/index.html</h1>"

@app.get("/api/stream")
async def stream(request: Request):
    """Endpoint SSE para enviar logs em tempo real."""
    queue = asyncio.Queue()
    
    with state.lock:
        state.clients.append(queue)
        # Envia os logs históricos primeiro para o cliente não começar vazio
        for log in state.logs[-50:]:
            await queue.put(log)
            
    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield f": keepalive\n\n" # Previne timeout de conexão
        finally:
            with state.lock:
                if queue in state.clients:
                    state.clients.remove(queue)
                    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/metrics")
async def get_metrics():
    """Retorna o estado atual das métricas."""
    with state.lock:
        return {
            "restarts": state.restarts,
            "code_errors": state.code_errors,
            "alerts": state.alerts,
            "zyte_ok": state.zyte_ok,
            "status": state.status
        }

def run_web_server():
    """Inicia o Uvicorn em uma thread daemon."""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

# =========================================================
# WATCHDOG CORE LOGIC
# =========================================================

def get_python_executable() -> str:
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
    if not stderr_output:
        return "runtime"
    stderr_lower = stderr_output.lower()
    for err_type in CODE_ERRORS:
        if err_type in stderr_lower:
            return "code"
    return "runtime"

def heal_dependencies(python_exe: str) -> None:
    state.add_log("info", "[Watchdog] Verificando integridade das dependências...")
    try:
        subprocess.run(
            [python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE, "-q"],
            check=True, env=CHILD_ENV,
        )
        state.add_log("info", "[Watchdog] Dependências sincronizadas.")
    except subprocess.CalledProcessError:
        state.add_log("warn", "[Watchdog] Falha na instalação. Purgando cache...")
        try:
            subprocess.run([python_exe, "-m", "pip", "cache", "purge"], check=True, env=CHILD_ENV)
            subprocess.run(
                [python_exe, "-m", "pip", "install", "-r", REQUIREMENTS_FILE, "-q"],
                check=True, env=CHILD_ENV,
            )
            state.add_log("info", "[Watchdog] Dependências sincronizadas após purga.")
        except Exception as e2:
            state.add_log("error", f"[Watchdog] Falha crítica ao curar dependências: {e2}")

def send_whatsapp_alert(message: str) -> None:
    global last_alert_time
    now = time.time()
    if now - last_alert_time < ALERT_COOLDOWN:
        state.add_log("dim", "[Watchdog] Alerta WhatsApp suprimido (cooldown).")
        return
    try:
        params = {"phone": CALLMEBOT_PHONE, "apikey": CALLMEBOT_APIKEY, "text": message}
        requests.get(CALLMEBOT_URL, params=params, timeout=10)
        last_alert_time = now
        state.update_metrics(alerts=state.alerts + 1)
        state.add_log("info", "[Watchdog] 📲 Alerta WhatsApp enviado.")
    except Exception as e:
        state.add_log("error", f"[Watchdog] Falha ao enviar alerta: {e}")

def guard():
    python_exe = get_python_executable()
    last_zyte_check = 0
    consecutive_code_errors = 0

    while True:
        # 1. Verificação Saúde Zyte
        if time.time() - last_zyte_check > ZYTE_CHECK_INTERVAL:
            state.add_log("info", "[Watchdog] Executando check-up periódico das APIs Zyte...")
            zyte_ok, zyte_msg = check_zyte_health()
            if not zyte_ok:
                send_whatsapp_alert(f"🚩 *ZYTE EXTRACTION ALERT* 🚩\nMotivo: `{zyte_msg}`")
                os.environ["ZYTE_DISABLED"] = "true"
                state.update_metrics(zyte_ok=False, status="ZYTE FALHOU")
                state.add_log("error", "[Watchdog] Motor Zyte PAUSADO devido a falha crítica.")
            else:
                if os.getenv("ZYTE_DISABLED") == "true":
                    os.environ["ZYTE_DISABLED"] = "false"
                    state.add_log("info", "[Watchdog] Motor Zyte RECUPERADO. Retomando uso.")
                state.update_metrics(zyte_ok=True)

            scrapy_ok, scrapy_msg = check_scrapy_cloud_health()
            if not scrapy_ok and os.getenv("SCRAPY_CLOUD_API_KEY"):
                send_whatsapp_alert(f"⚠️ *SCRAPY CLOUD ALERT* ⚠️\nMotivo: `{scrapy_msg}`")
            last_zyte_check = time.time()

        # 2. Auto Update
        try:
            if check_for_updates():
                heal_dependencies(python_exe)
        except Exception:
            pass

        # 3. Executar Servidor
        state.update_metrics(status="OPERACIONAL")
        state.add_log("info", "[Watchdog] Iniciando local_server.py...")
        try:
            process = subprocess.Popen(
                [python_exe, SERVER_SCRIPT], env=CHILD_ENV,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            
            while True:
                poll = process.poll()
                if poll is not None:
                    break
                time.sleep(10)

            if poll != 0:
                stderr_output = process.stderr.read() if process.stderr else ""
                error_type = classify_error(stderr_output)
                
                if error_type == "code":
                    consecutive_code_errors += 1
                    state.update_metrics(code_errors=consecutive_code_errors)
                    state.add_log("error", f"[Watchdog] ⛔ ERRO DE CÓDIGO detectado (tentativa {consecutive_code_errors})")
                    state.add_log("error", f"[Watchdog] Detalhes: {stderr_output[:150]}")
                    
                    if consecutive_code_errors >= 3:
                        send_whatsapp_alert("🛑 *WATCHDOG: ERRO DE CÓDIGO* 🛑\nReinícios parados. Correção manual necessária.")
                        state.update_metrics(status="PARADO - ERRO CODIGO")
                        state.add_log("error", "[Watchdog] 🛑 3 erros consecutivos. Parando.")
                        break
                    elif consecutive_code_errors == 1:
                        heal_dependencies(python_exe)
                else:
                    consecutive_code_errors = 0
                    state.update_metrics(restarts=state.restarts + 1, code_errors=0)
                    state.add_log("warn", "[Watchdog] ⚠️ Erro de runtime detectado. Reiniciando...")
                    send_whatsapp_alert(f"🚨 *WATCHDOG: RUNTIME ERROR* 🚨\nCode: {poll}. Reiniciando.")
            else:
                consecutive_code_errors = 0
                state.update_metrics(code_errors=0)
                
        except KeyboardInterrupt:
            state.add_log("dim", "[Watchdog] Interrompido pelo operador.")
            break
        except Exception as e:
            state.add_log("error", f"[Watchdog] Exceção no guardião: {e}")
        
        delay = RESTART_DELAY * min(consecutive_code_errors + 1, 5)
        state.add_log("dim", f"[Watchdog] Aguardando {delay}s antes do próximo ciclo...")
        time.sleep(delay)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Inicia o servidor web em background
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    print("🚀 Dashboard disponível em: http://localhost:8000")
    
    # Inicia o loop do guardião na thread principal
    print("🛡️ SENTINELA DEMOCRÁTICA - WATCHDOG v49.9")
    guard()
