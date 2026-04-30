import asyncio
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='networkidle', timeout=30000)
        content = await page.content()
        for term in ['ProfilePage', 'graphql', 'edge_owner_to_timeline_media', 'shortcode', 'window._sharedData', 'window.__additionalDataLoaded', 'window.__INITIAL_STATE__', 'application/ld+json']:
            print(term, term in content)
        # print some snippets around interesting terms
        for term in ['ProfilePage', 'graphql', 'edge_owner_to_timeline_media', 'shortcode']:
            idx = content.find(term)
            print('\n---', term, 'found at', idx)
            if idx != -1:
                print(content[idx-100:idx+260])
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
