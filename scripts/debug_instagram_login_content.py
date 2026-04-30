import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.instagram.com/accounts/login/', wait_until='domcontentloaded', timeout=30000)
        content = await page.content()
        print('len content', len(content))
        print('has username', 'name="username"' in content)
        print('has password', 'name="password"' in content)
        idx = content.find('name="username"')
        if idx != -1:
            print(content[idx-200:idx+400])
        else:
            print('username not found in raw HTML')
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
