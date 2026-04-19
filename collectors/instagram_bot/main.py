import os
import time
import schedule
import logging
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from instagram_bot.spiders.instagram import InstagramSpider

load_dotenv()

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("collector.log"),
        logging.StreamHandler()
    ]
)

def run_spider():
    logging.info("Starting Instagram Collection Job...")
    
    # Target usernames (should be configured via env or file)
    target_usernames = os.environ.get("TARGET_USERNAMES", "jairmessiasbolsonaro,lulaoficial")
    
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    
    process.crawl(InstagramSpider, usernames=target_usernames)
    process.start()
    
    logging.info("Collection Job Finished.")

def main():
    # Schedule jobs
    schedule.every().day.at("08:00").do(run_spider)
    schedule.every().day.at("20:00").do(run_spider)
    
    logging.info("Scheduler started. Waiting for jobs at 08:00 and 20:00...")
    
    # Run once at startup if desired for testing
    # run_spider()
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Collector stopped by user.")
    except Exception as e:
        logging.critical(f"Unexpected error: {e}")
