import asyncio
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        requests = []

        def on_request_finished(request):
            url = request.url
            if '/graphql/' in url or 'web_profile_info' in url or 'query_hash' in url:
                requests.append(url)

        page.on('requestfinished', on_request_finished)
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(3)
        print('matched requests:')
        for req in requests:
            print(req)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
