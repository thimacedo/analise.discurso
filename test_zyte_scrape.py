import asyncio
import logging
from scraper_zyte import InstagramScraperZyte

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestZyte")

async def test_zyte():
    scraper = InstagramScraperZyte("edinhosilvapt", max_posts=1)
    logger.info("Iniciando teste de coleta...")
    try:
        # Forçar uso do Browser para pegar o HTML
        browser_res = await scraper._zyte_request("https://www.instagram.com/edinhosilvapt/", {"User-Agent": "Mozilla/5.0"}, None, use_browser=True)
        html = browser_res.get("browserHtml", "")
        logger.info(f"HTML recebido (primeiros 500 chars): {html[:500]}")
        
        # Verificar se as tags JSON comuns existem
        has_shared_data = "_sharedData" in html
        has_additional_data = "__additionalData" in html
        logger.info(f"Contém _sharedData: {has_shared_data}")
        logger.info(f"Contém __additionalData: {has_additional_data}")
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")

if __name__ == "__main__":
    asyncio.run(test_zyte())
