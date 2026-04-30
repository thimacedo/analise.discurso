import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        async def on_console(msg):
            print('console', msg.type, msg.text)

        async def on_request_failed(request):
            print('failed', request.url, request.failure.error_text if request.failure else 'no failure info')

        page.on('console', on_console)
        page.on('requestfailed', on_request_failed)

        await page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)
        print('final url', page.url)
        print('username count', await page.locator('input[name="username"]').count())
        print('password count', await page.locator('input[name="password"]').count())
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
