import asyncio
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='networkidle', timeout=30000)
        scripts = await page.evaluate(r"""
            () => Array.from(document.querySelectorAll('script')).map(s => ({
                text: s.textContent || '',
                type: s.type || '',
                id: s.id || ''
            }))
        """)
        for idx, script in enumerate(scripts):
            if 'ProfilePage' in script['text'] or 'graphql' in script['text'] or 'shortcode' in script['text']:
                print('--- script', idx, 'type=', script['type'], 'id=', script['id'])
                print(script['text'][:2000])
                print('---\n')
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
