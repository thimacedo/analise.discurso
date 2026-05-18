import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("🔍 Testando imports...")

try:
    import scrapy
    print("✅ scrapy")
except ImportError as e:
    print(f"❌ scrapy: {e}")

try:
    import scrapy_playwright
    print("✅ scrapy_playwright")
except ImportError as e:
    print(f"❌ scrapy_playwright: {e}")

try:
    from playwright.sync_api import sync_playwright
    print("✅ playwright")
except ImportError as e:
    print(f"❌ playwright: {e}")

try:
    from sentinela_scrapy.spiders.instagram_api import InstagramAPISpider
    print("✅ instagram_api spider")
except ImportError as e:
    print(f"❌ instagram_api spider: {e}")

try:
    from sentinela_scrapy.spiders.instagram_dom import InstagramDOMSpider
    print("✅ instagram_dom spider")
except ImportError as e:
    print(f"❌ instagram_dom spider: {e}")
