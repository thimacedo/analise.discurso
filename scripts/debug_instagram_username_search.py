import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
        content = await page.content()
        print('username occurrences:', content.count('username'))
        idx = content.find('username')
        if idx != -1:
            print('first username at', idx)
            print(content[idx-100:idx+200])
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
