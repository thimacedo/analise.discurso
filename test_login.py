import asyncio
from playwright.async_api import async_playwright
import os
from dotenv import load_dotenv
load_dotenv()

async def test_login():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto('https://www.instagram.com/')
        await asyncio.sleep(5)
        print('Initial URL:', page.url)
        if '/accounts/login/' in page.url:
            await page.fill('input[name="username"]', os.getenv('IG_USER'))
            await page.fill('input[name="password"]', os.getenv('IG_PASS'))
            await page.click('button[type="submit"]')
            await page.wait_for_load_state('networkidle')
        print('Final URL:', page.url)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login())