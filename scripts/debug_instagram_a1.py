import asyncio
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='networkidle', timeout=30000)
        for suffix in ['', '?__a=1', '?__a=1&__d=dis', '?__a=1&__d=ajax']:
            try:
                result = await page.evaluate(rf"""
                    async () => {{
                        const response = await fetch(window.location.origin + window.location.pathname + '{suffix}');
                        const text = await response.text();
                        return {{status: response.status, ok: response.ok, snippet: text.slice(0, 2000)}};
                    }}
                """)
            except Exception as e:
                result = {{'error': str(e)}}
            print('suffix', suffix, result)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
