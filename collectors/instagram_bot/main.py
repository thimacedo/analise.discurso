import time
import schedule
import logging
import os
import subprocess
from datetime import datetime

# Configuração de log
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("collectors/instagram_bot/scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_spider():
    logger.info("🚀 Iniciando a execução do Scrapy (REST API v6.0)...")
    try:
        # Executa via subprocess para garantir isolamento do reactor e carregar settings corretamente
        cwd = os.path.abspath("collectors/instagram_bot")
        result = subprocess.run(
            ["scrapy", "crawl", "instagram"],
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            logger.info("✅ Execução do Scrapy finalizada com sucesso.")
        else:
            logger.error(f"❌ Falha no Scrapy: {result.stderr}")
            
    except Exception as e:
        logger.error(f"⚠️ Erro crítico ao executar o spider: {e}")

def main():
    # Agenda para rodar 2 vezes ao dia
    schedule.every().day.at("08:00").do(run_spider)
    schedule.every().day.at("20:00").do(run_spider)

    logger.info("🕵️ Agente de Extração Agendado (08:00 e 20:00). Aguardando...")
    
    # Executa uma rodada imediata para teste se desejado (opcional)
    # run_spider() 

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
