import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.instagram.com/', wait_until='networkidle', timeout=30000)
        print('root url', page.url)
        print('root title', await page.title())
        print('root cookies', await page.evaluate('() => document.cookie'))
        print('username_inputs', await page.locator('input[name="username"]').count())
        print('password_inputs', await page.locator('input[name="password"]').count())
        print('login_links', await page.locator('a[href="/accounts/login/"]').count())
        await page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
        print('login url', page.url)
        print('login title', await page.title())
        print('login username_inputs', await page.locator('input[name="username"]').count())
        print('login password_inputs', await page.locator('input[name="password"]').count())
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
