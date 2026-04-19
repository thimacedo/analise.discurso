# Scrapy settings for instagram_bot project

BOT_NAME = "instagram_bot"

SPIDER_MODULES = ["instagram_bot.spiders"]
NEWSPIDER_MODULE = "instagram_bot.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 2.5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 1
#CONCURRENT_REQUESTS_PER_IP = 1

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "X-IG-App-ID": "936619743392459",  # Common Instagram App ID
    "X-ASBD-ID": "129477",
    "X-IG-WWW-Claim": "0",
    "X-Requested-With": "XMLHttpRequest",
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "instagram_bot.pipelines.SupabasePipeline": 300,
}

# Enable and configure HTTP caching (disabled by default)
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings for the twisted reactor
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

FEED_EXPORT_ENCODING = "utf-8"
