import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
        buttons = await page.locator('button[type="submit"]').all()
        print('button count', len(buttons))
        for idx, button in enumerate(buttons):
            print('button', idx)
            print(await button.get_attribute('outerHTML'))
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
