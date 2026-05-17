"""
PASA v49.5 - Instagram Scrapy Worker
Opção de alta performance via Scrapy Crawler.
MANTIDO DESATIVADO (OFF) POR PADRÃO.
"""
import os
import subprocess
from app.workers.base_worker import BaseWorker

class InstagramScrapyWorker(BaseWorker):
    def __init__(self):
        super().__init__(platform="instagram_scrapy")
        self.worker_id = "InstagramScrapyWorker"

    def run(self, target: str):
        """
        Executa o spider do Scrapy para um alvo específico.
        Nota: Este worker está desativado no fluxo principal do local_server.
        """
        print(f"[ScrapyWorker] 🕷️ Iniciando coleta via Scrapy para: {target}")
        
        # O spider 'instagram' em sentinela_scraper/spiders/instagram.py 
        # já tem lógica para buscar alvos, mas podemos forçar um alvo específico 
        # via argumentos do Scrapy se necessário.
        
        try:
            # Comando para rodar o Scrapy a partir da raiz do projeto
            # Usamos -a para passar o alvo diretamente se o spider for adaptado
            # Por enquanto, ele usa a fila do banco de dados.
            command = ["scrapy", "crawl", "instagram"]
            
            # Executa o processo de forma síncrona
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                print(f"[ScrapyWorker] ✅ Ciclo Scrapy finalizado com sucesso.")
                return True
            else:
                print(f"[ScrapyWorker] ❌ Erro no Scrapy: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ScrapyWorker] 💥 Falha ao disparar Scrapy: {e}")
            return False

# Esta instância não é importada pelo local_server.py por padrão.
