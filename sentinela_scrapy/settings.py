BOT_NAME = 'sentinela_scrapy'
SPIDER_MODULES = ['sentinela_scrapy.spiders']
NEWSPIDER_MODULE = 'sentinela_scrapy.spiders'

# Obedece robots.txt (Instagram bloqueia, mas é boa prática tentar)
ROBOTSTXT_OBEY = False

# Delay humano obrigatório (1.5 a 3.5s entre requests)
DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True

# Auto-Throttling (Scrapy ajusta a velocidade sozinho se o site ficar lento)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2.0
AUTOTHROTTLE_MAX_DELAY = 10.0

# User Agent rotativo
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'

# Desabilita estatísticas e logs excessivos para economizar memória
LOG_LEVEL = 'WARNING'
STATS_CLASS = 'scrapy.statscollectors.DummyStatsCollector'

# Pipeline para limpar o JSON de saída
ITEM_PIPELINES = {
   'sentinela_scrapy.pipelines.CleanCommentPipeline': 300,
}
