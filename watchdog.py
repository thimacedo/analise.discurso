import os
import time
import logging
import subprocess
from dotenv import load_dotenv

# --- Configuração Inicial ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SentinelaWatchdog")

# Importa as funções de verificação do módulo unificado
try:
    from core.zyte_checker import check_zyte_health, check_scrapy_cloud_health
    from core.alert_manager import send_whatsapp_alert
except ImportError:
    logger.critical("Erro fatal: Não foi possível importar os módulos de verificação ou alerta. O Watchdog não pode operar.")
    exit(1)


# --- Constantes de Controle ---
ZYTE_CHECK_INTERVAL = 1800  # 30 minutos
SERVER_SCRIPT = "local_server.py"
PYTHON_EXECUTABLE = "python" # ou "python3" dependendo do seu sistema

def guard():
    """
    Função principal que monitora o servidor local e a saúde dos serviços,
    reiniciando o servidor se ele cair.
    """
    server_process = None
    last_zyte_check = 0

    while True:
        # 1. Gerenciamento do Processo do Servidor Local
        if server_process is None or server_process.poll() is not None:
            if server_process is not None:
                logger.error("[Watchdog] O servidor local (local_server.py) caiu! Reiniciando em 10 segundos...")
                send_whatsapp_alert("🔥 *SENTINELA DOWN* 🔥

O processo `local_server.py` caiu e será reiniciado. Verifique os logs para a causa raiz.")
                time.sleep(10)
            
            logger.info(f"[Watchdog] Iniciando o servidor local: {SERVER_SCRIPT}")
            server_process = subprocess.Popen([PYTHON_EXECUTABLE, SERVER_SCRIPT])

        # 2. Verificação de Saúde das APIs Externas (Zyte e Scrapy Cloud)
        if time.time() - last_zyte_check > ZYTE_CHECK_INTERVAL:
            logger.info("[Watchdog] Executando check-up periódico das APIs Zyte...")
            
            # Check 2.1: Zyte Extraction API
            zyte_ok, zyte_msg = check_zyte_health()
            if not zyte_ok:
                send_whatsapp_alert(f"🚩 *ZYTE EXTRACTION ALERT* 🚩
Motivo: `{zyte_msg}`")
                os.environ["ZYTE_DISABLED"] = "true"
                logger.warning("[Watchdog] Motor Zyte PAUSADO devido a falha crítica.")
            else:
                if os.getenv("ZYTE_DISABLED") == "true":
                    # Se o serviço voltou, reabilita e notifica
                    os.environ["ZYTE_DISABLED"] = "false"
                    logger.info("[Watchdog] Motor Zyte RECUPERADO. Retomando uso.")
                    send_whatsapp_alert("✅ *ZYTE EXTRACTION OK* ✅

O serviço da Zyte API foi restaurado. O motor de extração foi reativado.")
            
            # Check 2.2: Scrapy Cloud (Apenas alerta, não pausa nada)
            scrapy_ok, scrapy_msg = check_scrapy_cloud_health()
            if not scrapy_ok:
                # Alerta apenas se a chave existir (ou seja, se o sistema estiver em uso)
                if os.getenv("SCRAPY_CLOUD_API_KEY"):
                    send_whatsapp_alert(f"⚠️ *SCRAPY CLOUD ALERT* ⚠️
Motivo: `{scrapy_msg}`")
            
            last_zyte_check = time.time()

        time.sleep(60)  # Verifica o status do processo do servidor a cada minuto

if __name__ == "__main__":
    try:
        guard()
    except KeyboardInterrupt:
        logger.info("
🛑 Watchdog finalizado pelo usuário.")
    except Exception as e:
        logger.critical(f"Erro fatal no Watchdog: {e}")
        send_whatsapp_alert(f"💥 *WATCHDOG CRASHED* 💥

O próprio watchdog encontrou um erro fatal e parou: `{e}`")
