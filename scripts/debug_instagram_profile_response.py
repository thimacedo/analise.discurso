import os
import asyncio
from dotenv import load_dotenv
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

def is_profile_query(request):
    return request.url.startswith('https://www.instagram.com/graphql/query') and 'doc_id=25858451687162830' in request.post_data

async def main():
    load_dotenv()
    ig_user = os.getenv('IG_USER')
    ig_pass = os.getenv('IG_PASS')
    print(f'IG_USER: {ig_user is not None}, IG_PASS: {ig_pass is not None}')
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

        async def on_response(response):
            request = response.request
            try:
                if request.url.startswith('https://www.instagram.com/graphql/query'):
                    print('GRAPHQL RESPONSE URL', response.url)
                    print('POST DATA', request.post_data if request.post_data else 'none')
                    if 'doc_id=27077551658551360' in (request.post_data or ''):
                        print('PROFILE QUERY FOUND')
                        text = await response.text()
                        print('STATUS', response.status)
                        print(text[:5000])
            except Exception as e:
                print('error response handler', e)

        page.on('response', on_response)
        print('Going to login page...')
        await page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
        print('Login page loaded')
        if await page.locator('input[name="email"]').count() > 0:
            await page.fill('input[name="email"]', ig_user)
        elif await page.locator('input[name="username"]').count() > 0:
            await page.fill('input[name="username"]', ig_user)
        await page.fill('input[name="pass"]', ig_pass)
        print('Submitting login...')
        await page.locator('input[name="pass"]').press('Enter')
        await page.wait_for_timeout(10000)
        print('After login, going to profile...')
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(10000)
        print('Profile page loaded')
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())