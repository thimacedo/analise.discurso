import os
import sys
from dotenv import load_dotenv
from scrapy.cmdline import execute

# Caminho para o .env na raiz do projeto
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../.env'))
load_dotenv(dotenv_path)

# Verifica se carregou
if not os.getenv("INSTAGRAM_SESSIONID"):
    print("❌ ERRO: INSTAGRAM_SESSIONID não encontrado no .env")
    sys.exit(1)

print(f"🚀 Iniciando Scrapy Stealth com Session: {os.getenv('INSTAGRAM_SESSIONID')[:10]}...")

# Muda para o diretório do bot para o Scrapy achar o scrapy.cfg
os.chdir(os.path.dirname(__file__))

# Executa o Scrapy
sys.argv = ['scrapy', 'crawl', 'instagram']
execute()
