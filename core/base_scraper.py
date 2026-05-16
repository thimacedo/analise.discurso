import logging
import time
import random
from abc import ABC, abstractmethod

# Configuração de logging estruturado para o sistema
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SentinelaScraper")

class SentinelaScraper(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logger.getChild(name)

    def _human_pause(self, min_sec=10, max_sec=30):
        pause = random.uniform(min_sec, max_sec)
        self.logger.info(f"Pausa humana de {pause:.2f} segundos...")
        time.sleep(pause)

    @abstractmethod
    def login(self):
        """Implementação específica de login por rede social."""
        pass

    @abstractmethod
    def scrape(self, target: str):
        """Implementação específica de scraping."""
        pass
