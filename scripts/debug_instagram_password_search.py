import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
        content = await page.content()
        print('password occurrences:', content.count('password'))
        idx = content.find('password')
        if idx != -1:
            print(content[idx-100:idx+200])
        else:
            print('password not found in raw HTML')
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
