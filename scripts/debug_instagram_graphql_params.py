import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

async def main():
    load_dotenv()
    ig_user = os.getenv('IG_USER')
    ig_pass = os.getenv('IG_PASS')
    if not ig_user or not ig_pass:
        print('missing IG_USER/IG_PASS')
        return

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            locale='pt-BR',
            extra_http_headers={
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
            }
        )
        page = await context.new_page()

        async def on_request(request):
            if '/graphql/query' in request.url or 'web_profile_info' in request.url:
                print('REQUEST URL', request.url)
                print('METHOD', request.method)
                print('POST', await request.post_data() if request.method == 'POST' else 'none')
                print('HEADERS', request.headers)
                print('---')

        page.on('request', on_request)
        await page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
        if await page.locator('input[name="email"]').count() > 0:
            await page.fill('input[name="email"]', ig_user)
        elif await page.locator('input[name="username"]').count() > 0:
            await page.fill('input[name="username"]', ig_user)
        await page.fill('input[name="pass"]', ig_pass)
        await page.locator('input[name="pass"]').press('Enter')
        await page.wait_for_timeout(10000)
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(8000)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
