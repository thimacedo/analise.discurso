
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        print('playwright_loaded')
        browser = await pw.chromium.launch(headless=True)
        print('chromium_launched')
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
