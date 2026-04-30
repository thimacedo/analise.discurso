import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
        content = await page.content()
        print('submit occurrences:', content.count('type="submit"'))
        idx = content.find('type="submit"')
        if idx != -1:
            print(content[idx-200:idx+400])
        print('button label snippet around login button:')
        idx2 = content.find('button', idx-200 if idx!=-1 else 0)
        if idx2 != -1:
            print(content[idx2:idx2+300])
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
