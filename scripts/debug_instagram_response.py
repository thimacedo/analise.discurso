import asyncio
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        matched = []

        async def on_request_finished(request):
            url = request.url
            if 'https://www.instagram.com/graphql/query' in url and 'query_id=9957820854288654' in url:
                try:
                    response = await request.response()
                    if response:
                        text = await response.text()
                        print('URL:', url)
                        print('STATUS:', response.status)
                        print('BODY PREVIEW:', text[:2000])
                        matched.append(True)
                except Exception as e:
                    print('failed reading response', e)

        page.on('requestfinished', on_request_finished)
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='networkidle', timeout=30000)
        await asyncio.sleep(5)
        if not matched:
            print('no matching GraphQL response captured')
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
