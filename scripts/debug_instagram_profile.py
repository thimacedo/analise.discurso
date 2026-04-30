import asyncio
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='networkidle', timeout=30000)
        print('title:', await page.title())
        shared_data = await page.evaluate(r"""
            () => {
                const scripts = Array.from(document.querySelectorAll('script'));
                const data = [];
                for (const script of scripts) {
                    const text = script.textContent || '';
                    if (text.includes('window._sharedData')) {
                        data.push('window._sharedData');
                    }
                    if (text.includes('window.__additionalDataLoaded')) {
                        data.push('window.__additionalDataLoaded');
                    }
                    if (text.includes('application/ld+json')) {
                        data.push('application/ld+json');
                    }
                }
                return data;
            }
        """)
        print('matched scripts:', shared_data)
        html = await page.content()
        print('page length', len(html))
        print('contains _sharedData:', '_sharedData' in html)
        print('contains __additionalDataLoaded:', '__additionalDataLoaded' in html)
        print('contains window.__INITIAL_STATE__:', 'window.__INITIAL_STATE__' in html)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
