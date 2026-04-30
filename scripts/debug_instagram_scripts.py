import asyncio
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='networkidle', timeout=30000)
        scripts = await page.evaluate(r"""
            () => {
                return Array.from(document.querySelectorAll('script')).map(s => ({
                    type: s.type || null,
                    id: s.id || null,
                    text_snippet: (s.textContent || '').slice(0, 500)
                }))
            }
        """)
        for idx, script in enumerate(scripts):
            print(f'--- script {idx} type={script["type"]} id={script["id"]}')
            print(script['text_snippet'])
            print('---\n')
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
