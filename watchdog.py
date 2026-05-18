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
from typing import Tuple, Dict, Any, List

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

CODE_ERRORS = [
    "importerror", "modulenotfounderror", "syntaxerror",
    "indentationerror", "attributeerror", "nameerror", "typeerror",
]

# --- Variáveis de Controle ---
last_alert_time = 0
last_sent_message = ""
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
        self.logs: List[Dict[str, str]] = [] # Guarda os últimos N logs para enviar aos novos clientes
        self.clients: List[asyncio.Queue] = [] # Filas asyncio para SSE
        
    def add_log(self, level: str, message: str) -> None:
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
                    
    def update_metrics(self, **kwargs: Any) -> None:
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
    """Dispara alerta via WhatsApp usando CallMeBot, com cooldown e bloqueio anti-spam."""
    global last_alert_time, last_sent_message
    
    if message == last_sent_message:
        state.add_log("dim", "[Watchdog] Alerta ignorado (anti-spam: idêntico ao anterior).")
        return
        
    now = time.time()
    if now - last_alert_time < ALERT_COOLDOWN:
        state.add_log("dim", "[Watchdog] Alerta WhatsApp suprimido (cooldown ativo).")
        return
        
    try:
        params = {"phone": CALLMEBOT_PHONE, "apikey": CALLMEBOT_APIKEY, "text": message}
        requests.get(CALLMEBOT_URL, params=params, timeout=10)
        last_alert_time = now
        last_sent_message = message
        state.update_metrics(alerts=state.alerts + 1)
        state.add_log("info", "[Watchdog] 📲 Alerta WhatsApp enviado.")
    except Exception as e:
        state.add_log("error", f"[Watchdog] Falha ao enviar alerta: {e}")

def check_api_health() -> None:
    """Verifica a saúde das APIs Zyte e Scrapy Cloud e toma ações preventivas."""
    state.add_log("info", "[Watchdog] Executando check-up periódico das APIs Zyte e Scrapy Cloud...")

    # Check 1: Zyte Extraction API
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

    # Check 2: Scrapy Cloud (apenas alerta)
    scrapy_ok, scrapy_msg = check_scrapy_cloud_health()
    if not scrapy_ok and os.getenv("SCRAPY_CLOUD_API_KEY"):
        send_whatsapp_alert(f"⚠️ *SCRAPY CLOUD ALERT* ⚠️\nMotivo: `{scrapy_msg}`")

def heal_runtime_error(stderr_output: str) -> str:
    """
    Analisa o erro de runtime e toma ações corretivas antes de reiniciar.
    Retorna: 'restart', 'wait' ou 'fatal'
    """
    if not stderr_output:
        return "restart"
    
    stderr_lower = stderr_output.lower()

    # 1. Erro Fatal: Out of Memory (OOM)
    if "out of memory" in stderr_lower or "oom-killer" in stderr_lower or "cannot allocate memory" in stderr_lower:
        state.add_log("error", "[Watchdog] 🛑 OOM Detectado! Reinícios parados para proteger o sistema.")
        send_whatsapp_alert("🛑 *WATCHDOG: OOM FATAL* 🛑\nMemória esgotada. Sistema pausado para evitar crash do PC.")
        state.update_metrics(status="PARADO - OOM")
        return "fatal"

    # 2. Erro de Conexão (Supabase/APIs fora do ar)
    if "connectionrefusederror" in stderr_lower or "supabase" in stderr_lower and ("timeout" in stderr_lower or "refused" in stderr_lower):
        state.add_log("warn", "[Watchdog] ⏸️ Banco de dados offline. Aguardando 5 minutos antes de tentar.")
        time.sleep(300) # Pausa longa para não esmurrar o Supabase
        return "wait"

    # 3. Erro de Playwright (Navegador travou)
    if "browser closed" in stderr_lower or "playwright" in stderr_lower and ("crash" in stderr_lower or "timeout" in stderr_lower):
        state.add_log("warn", "[Watchdog] 🧹 Playwright crashou. Limpando processos órfãos do Chrome...")
        try:
            # Tenta matar processos do Chrome/Chromium que ficaram presos
            if os.name == 'nt':
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
                subprocess.run(["taskkill", "/F", "/IM", "chromium.exe"], capture_output=True)
            else:
                subprocess.run(["pkill", "-f", "chrome"], capture_output=True)
        except Exception:
            pass
        return "restart"
        
    return "restart"

def handle_process_failure(poll: int, stderr_output: str, consecutive_code_errors: int, python_exe: str) -> Tuple[bool, int]:
    """
    Trata a falha do processo filho (local_server.py).
    Retorna uma tupla: (deve_parar_loop, consecutive_code_errors atualizado)
    """
    error_type = classify_error(stderr_output)
    
    # LOG OBRIGATÓRIO: Mostra o motivo real do crash no Dashboard
    if stderr_output:
        state.add_log("dim", f"[Watchdog] STDERR: {stderr_output[:250]}...")
    
    if error_type == "code":
        consecutive_code_errors += 1
        state.update_metrics(code_errors=consecutive_code_errors)
        state.add_log("error", f"[Watchdog] ⛔ ERRO DE CÓDIGO detectado (tentativa {consecutive_code_errors})")
        
        if consecutive_code_errors >= 3:
            send_whatsapp_alert("🛑 *WATCHDOG: ERRO DE CÓDIGO* 🛑\nReinícios parados. Correção manual necessária.")
            state.update_metrics(status="PARADO - ERRO CODIGO")
            state.add_log("error", "[Watchdog] 🛑 3 erros consecutivos. Parando auto-recuperação.")
            return True, consecutive_code_errors
        elif consecutive_code_errors == 1:
            heal_dependencies(python_exe)
    else:
        consecutive_code_errors = 0
        state.update_metrics(restarts=state.restarts + 1, code_errors=0)
        state.add_log("warn", "[Watchdog] ⚠️ Erro de runtime detectado. Analisando autocura...")
        
        # NOVO: Tenta curar o erro de runtime antes de reiniciar
        healing_action = heal_runtime_error(stderr_output)
        if healing_action == "fatal":
            return True, consecutive_code_errors # Para o Watchdog (ex: OOM)
        elif healing_action == "wait":
            pass # Já esperou dentro da função
        else:
            send_whatsapp_alert(f"🚨 *WATCHDOG: RUNTIME ERROR* 🚨\nCode: {poll}. Reiniciando.")

    return False, consecutive_code_errors

def guard() -> None:
    """Loop principal do guardião."""
    python_exe = get_python_executable()
    last_zyte_check = 0
    consecutive_code_errors = 0

    while True:
        # 1. Verificação Saúde APIs
        if time.time() - last_zyte_check > ZYTE_CHECK_INTERVAL:
            check_api_health()
            last_zyte_check = time.time()

        # 2. Auto Update
        try:
            if check_for_updates():
                heal_dependencies(python_exe)
        except Exception:
            pass

        # 3. Executar Servidor Local
        state.update_metrics(status="OPERACIONAL")
        state.add_log("info", "[Watchdog] Iniciando local_server.py...")
        try:
            process = subprocess.Popen(
                [python_exe, SERVER_SCRIPT], env=CHILD_ENV,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            )
            
            # Monitora processo rodando
            while True:
                poll = process.poll()
                if poll is not None:
                    break
                time.sleep(10)

            # Processo terminou
            if poll != 0:
                stderr_output = process.stderr.read() if process.stderr else ""
                should_stop, consecutive_code_errors = handle_process_failure(poll, stderr_output, consecutive_code_errors, python_exe)
                if should_stop:
                    break
            else:
                consecutive_code_errors = 0
                state.update_metrics(code_errors=0)
                
        except KeyboardInterrupt:
            state.add_log("dim", "[Watchdog] Interrompido pelo operador.")
            break
        except Exception as e:
            state.add_log("error", f"[Watchdog] Exceção no guardião: {e}")
        
        # Delay adaptativo antes de reiniciar
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
