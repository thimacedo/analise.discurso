import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

BOT_NAME = "instagram_bot"
SPIDER_MODULES = ["instagram_bot.spiders"]
NEWSPIDER_MODULE = "instagram_bot.spiders"

ROBOTSTXT_OBEY = False

# Evita bloqueios por taxa
DOWNLOAD_DELAY = 2.5
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 1

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

# --- MIDDLEWARES DE EVASÃO (ELITE) ---
DOWNLOADER_MIDDLEWARES = {
    'instagram_bot.middlewares.BrowserbaseProxyMiddleware': 100,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 200,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# Configurações do Browserbase (via .env)
BROWSERBASE_API_KEY = os.environ.get("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.environ.get("BROWSERBASE_PROJECT_ID")

# Configurações de atraso para mimetizar humano
DOWNLOAD_DELAY = 3.5
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 1 # Manter baixo para evitar detecção de padrão

# --- CONFIGURAÇÕES SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
INSTAGRAM_SESSIONID = os.environ.get("INSTAGRAM_SESSIONID")

