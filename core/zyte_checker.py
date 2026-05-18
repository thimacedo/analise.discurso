"""
PASA v49.9 - Zyte & Scrapy Cloud Health Checkers
Verifica a integridade da conexão com as APIs Zyte para o Watchdog.
Inclui micro-retries e classificação de erros críticos (Zyte Best Practices).
"""
import httpx
import os
import logging
import time
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ZyteChecker")

def check_zyte_health(max_retries=3, delay_seconds=5):
    """Valida se a chave do Zyte Extraction API está ativa e há conectividade."""
    zyte_key = os.getenv("ZYTE_API_KEY")
    if not zyte_key:
        return False, "ZYTE_API_KEY ausente no .env"

    url = "https://api.zyte.com/v1/extract"
    payload = {"url": "https://toscrape.com", "httpResponseBody": True}

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.post(url, auth=(zyte_key, ""), json=payload)

            if response.status_code == 200:
                logger.info("✅ Conectado com sucesso ao Zyte Extraction API.")
                return True, "Conectado"
            elif response.status_code in {401, 403, 451}:
                logger.error(f"Erro crítico Zyte API {response.status_code}: {response.text[:100]}")
                return False, f"Erro crítico {response.status_code}: {response.text[:100]}"
            else:
                logger.warning(f"Tentativa {attempt+1}/{max_retries} - Erro Zyte API {response.status_code}: {response.text[:100]}")
        except httpx.TimeoutException:
            logger.warning(f"Tentativa {attempt+1}/{max_retries} - Timeout na conexão Zyte API.")
        except httpx.RequestError as e:
            logger.warning(f"Tentativa {attempt+1}/{max_retries} - Erro na requisição Zyte API: {str(e)}")

        if attempt < max_retries - 1:
            time.sleep(delay_seconds)

    return False, f"Falha persistente após {max_retries} tentativas."


def check_scrapy_cloud_health(max_retries=3, delay_seconds=5):
    """Valida se a chave do Scrapy Cloud está ativa e o projeto é acessível."""
    scrapy_key = os.getenv("SCRAPY_CLOUD_API_KEY")
    if not scrapy_key:
        # Se não tem chave, pula silenciosamente (Scrapy está em Standby)
        return True, "Scrapy Cloud em Standby (sem chave)"

    auth = (scrapy_key, "")
    url = "https://app.zyte.com/api/projects/list.json"

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(url, auth=auth)

            if response.status_code == 200:
                projects = response.json().get("projects", [])
                if projects:
                    logger.info(f"✅ Scrapy Cloud OK. {len(projects)} projetos encontrados.")
                    return True, f"Scrapy Cloud OK - {len(projects)} projetos"
                else:
                    logger.warning("⚠️ Scrapy Cloud acessível, mas nenhum projeto encontrado.")
                    return False, "Scrapy Cloud OK mas sem projetos"
            elif response.status_code in {401, 403}:
                logger.error(f"Erro crítico Scrapy Cloud {response.status_code}: {response.text[:100]}")
                return False, f"Erro crítico Scrapy Cloud {response.status_code}"
            else:
                logger.warning(f"Tentativa {attempt+1}/{max_retries} - Scrapy Cloud HTTP {response.status_code}: {response.text[:100]}")
        except httpx.TimeoutException:
            logger.warning(f"Tentativa {attempt+1}/{max_retries} - Timeout na conexão Scrapy Cloud.")
        except httpx.RequestError as e:
            logger.warning(f"Tentativa {attempt+1}/{max_retries} - Erro na requisição Scrapy Cloud: {str(e)}")

        if attempt < max_retries - 1:
            time.sleep(delay_seconds)

    return False, f"Falha Scrapy Cloud após {max_retries} tentativas."
