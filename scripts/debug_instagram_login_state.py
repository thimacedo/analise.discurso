import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.instagram.com/', wait_until='networkidle', timeout=30000)
        print('title:', await page.title())
        username_inputs = await page.locator('input[name="username"]').count()
        password_inputs = await page.locator('input[name="password"]').count()
        login_links = await page.locator('a[href="/accounts/login/"]').count()
        print('username_inputs', username_inputs)
        print('password_inputs', password_inputs)
        print('login_links', login_links)
        print('body length', len(await page.content()))
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
