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
