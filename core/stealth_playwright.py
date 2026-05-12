
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import random
from playwright.async_api import async_playwright, BrowserContext

class StealthBrowser:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.user_agents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"]

    async def get_stealth_context(self, playwright, proxy: dict = None) -> BrowserContext:
        browser = await playwright.chromium.launch(headless=self.headless, proxy=proxy)
        context = await browser.new_context(user_agent=random.choice(self.user_agents))
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
        return context
