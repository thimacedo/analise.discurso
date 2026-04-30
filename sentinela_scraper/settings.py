BOT_NAME = "sentinela_scraper"
SPIDER_MODULES = ["sentinela_scraper.spiders"]
NEWSPIDER_MODULE = "sentinela_scraper.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Delay para simular humano (v18.0 Resilience)
DOWNLOAD_DELAY = 5.0
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 1
CONCURRENT_REQUESTS = 1

ITEM_PIPELINES = {
    "sentinela_scraper.pipelines.SupabasePipeline": 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
