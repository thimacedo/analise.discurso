import httpx
import os
import logging
import time
from dotenv import load_dotenv

# --- Configuração Inicial ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SentinelaWatchdog")

# --- Constantes ---
WATCHDOG_INTERVAL = 1800  # 30 minutos
ZYTE_API_KEY = os.getenv("ZYTE_API_KEY")
SCRAPY_CLOUD_API_KEY = os.getenv("SCRAPY_CLOUD_API_KEY")
SCRAPY_CLOUD_BASE_API = "https://app.zyte.com/api"
CALLMEBOT_PHONE = os.getenv("CALLMEBOT_PHONE")
CALLMEBOT_API_KEY = os.getenv("CALLMEBOT_API_KEY")

# --- Funções de Verificação de Saúde ---

def check_zyte_health(max_retries=3, delay_seconds=5):
    """Valida a conectividade e autenticação com a Zyte API."""
    if not ZYTE_API_KEY:
        return False, "ZYTE_API_KEY ausente no .env"

    url = "https://api.zyte.com/v1/extract"
    payload = {"url": "https://toscrape.com", "httpResponseBody": True}

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(url, auth=(ZYTE_API_KEY, ""), json=payload)

            if response.status_code == 200:
                return True, "Conectado"
            elif response.status_code in {401, 403}:
                logger.error(f"Erro crítico Zyte API {response.status_code}: Chave de API inválida ou suspensa.")
                return False, f"Erro crítico de autenticação ({response.status_code})."
            else:
                logger.warning(f"Tentativa {attempt+1}/{max_retries} - Erro Zyte API {response.status_code}")
        except httpx.TimeoutException:
            logger.warning(f"Tentativa {attempt+1}/{max_retries} - Timeout na conexão Zyte API.")
        except httpx.RequestError as e:
            logger.warning(f"Tentativa {attempt+1}/{max_retries} - Erro de rede ao conectar com Zyte API: {e}")

        if attempt < max_retries - 1:
            time.sleep(delay_seconds)
    
    return False, f"Falha de conexão após {max_retries} tentativas."

def check_scrapy_cloud_health(max_retries=3, delay_seconds=5):
    """Valida a conectividade e autenticação com a Scrapy Cloud API."""
    if not SCRAPY_CLOUD_API_KEY:
        return False, "SCRAPY_CLOUD_API_KEY ausente no .env"

    auth = (SCRAPY_CLOUD_API_KEY, "")
    url = f"{SCRAPY_CLOUD_BASE_API}/projects/list.json"

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, auth=auth)
            
            if response.status_code == 200:
                projects = response.json().get("projects", [])
                logger.info(f"Scrapy Cloud alcançável. {len(projects)} projetos encontrados.")
                return True, f"{len(projects)} projetos encontrados"
            elif response.status_code in {401, 403}:
                logger.error(f"Erro crítico Scrapy Cloud {response.status_code}: Chave de API inválida ou sem permissão.")
                return False, f"Erro crítico de autenticação ({response.status_code})."
            else:
                logger.warning(f"Tentativa {attempt+1}/{max_retries} - Scrapy Cloud HTTP {response.status_code}")
        except httpx.TimeoutException:
            logger.warning(f"Tentativa {attempt+1}/{max_retries} - Timeout na conexão Scrapy Cloud.")
        except httpx.RequestError as e:
            logger.warning(f"Tentativa {attempt+1}/{max_retries} - Erro de rede ao conectar com Scrapy Cloud: {e}")

        if attempt < max_retries - 1:
            time.sleep(delay_seconds)

    return False, f"Falha de conexão após {max_retries} tentativas."

# --- Sistema de Alerta ---

def send_whatsapp_alert(message: str):
    """Envia um alerta via CallMeBot para o WhatsApp."""
    if not (CALLMEBOT_PHONE and CALLMEBOT_API_KEY):
        logger.error("Variáveis de ambiente para o CallMeBot não configuradas. Alerta não enviado.")
        return

    try:
        url = "https://api.callmebot.com/whatsapp.php"
        params = {"phone": CALLMEBOT_PHONE, "text": message, "apikey": CALLMEBOT_API_KEY}
        with httpx.Client() as client:
            client.get(url, params=params)
        logger.info("Alerta WhatsApp enviado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao enviar alerta WhatsApp: {e}")

# --- Loop Principal do Watchdog ---

def watchdog_loop():
    logger.info("🚀 Sentinela Watchdog INICIADO. Monitorando saúde dos serviços...")
    while True:
        # 1. Verificar Zyte API
        logger.info("Verificando saúde: Zyte API...")
        zyte_status, zyte_msg = check_zyte_health()
        if not zyte_status:
            alert_text = f"🚨 *ALERTA SENTINELA* 🚨

*Serviço*: Zyte API
*Status*: INDISPONÍVEL
*Motivo*: {zyte_msg}

A coleta de dados pode estar comprometida."
            logger.error(alert_text)
            send_whatsapp_alert(alert_text)
        else:
            logger.info(f"✅ Saúde OK: Zyte API ({zyte_msg})")

        # Pausa breve entre as checagens
        time.sleep(10)

        # 2. Verificar Scrapy Cloud
        logger.info("Verificando saúde: Scrapy Cloud...")
        sc_status, sc_msg = check_scrapy_cloud_health()
        if not sc_status:
            alert_text = f"🚨 *ALERTA SENTINELA* 🚨

*Serviço*: Scrapy Cloud
*Status*: INDISPONÍVEL
*Motivo*: {sc_msg}

O deploy de spiders pode falhar."
            logger.error(alert_text)
            send_whatsapp_alert(alert_text)
        else:
            logger.info(f"✅ Saúde OK: Scrapy Cloud ({sc_msg})")

        logger.info(f"Próxima verificação em {WATCHDOG_INTERVAL / 60:.0f} minutos.")
        time.sleep(WATCHDOG_INTERVAL)

if __name__ == "__main__":
    try:
        watchdog_loop()
    except KeyboardInterrupt:
        logger.info("
🛑 Watchdog finalizado manualmente.")
