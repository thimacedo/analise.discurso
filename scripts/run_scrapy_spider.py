import sys
import os
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

def run_spider(spider_name: str, username: str, sessionid: str, max_posts: str, output_file: str):
    """Executa um spider do Scrapy."""
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'sentinela_scrapy.settings')
    settings = get_project_settings()
    
    # Atualiza settings para salvar no arquivo especificado
    settings.update({
        'FEEDS': {
            output_file: {
                'format': 'json',
                'overwrite': True,
                'encoding': 'utf-8',
                'item_export_kwargs': {
                    'ensure_ascii': False,
                    'indent': 2
                }
            }
        }
    })
    
    process = CrawlerProcess(settings)
    
    # Argumentos comuns
    kwargs = {
        'username': username,
        'sessionid': sessionid,
        'max_posts': int(max_posts)
    }
    
    # Adiciona max_comments apenas para DOM
    if spider_name == 'instagram_dom':
        kwargs['max_comments'] = 50
    
    process.crawl(spider_name, **kwargs)
    process.start()

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("❌ Uso: python run_scrapy_spider.py <spider_name> <username> <sessionid> <max_posts> <output_file>")
        print("Spiders disponíveis: instagram_api, instagram_dom")
        sys.exit(1)
    
    run_spider(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
