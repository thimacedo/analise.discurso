import asyncio
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

async def main():
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
        await page.goto('https://www.instagram.com/accounts/login/', wait_until='networkidle', timeout=30000)
        print('login page url', page.url)
        print('input email', await page.locator('input[name="email"]').count())
        print('input username', await page.locator('input[name="username"]').count())
        print('input pass', await page.locator('input[name="pass"]').count())
        print('button submit', await page.locator('button[type="submit"]').count())
        if await page.locator('input[name="email"]').count() > 0:
            await page.fill('input[name="email"]', 'test@example.com')
        elif await page.locator('input[name="username"]').count() > 0:
            await page.fill('input[name="username"]', 'test')
        await page.fill('input[name="pass"]', 'x')
        await page.locator('input[name="pass"]').press('Enter')
        await page.wait_for_timeout(5000)
        print('after submit url', page.url)
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='domcontentloaded', timeout=30000)
        await page.wait_for_timeout(5000)
        print('profile url', page.url)
        content = await page.content()
        print('contains window._sharedData', 'window._sharedData' in content)
        print('contains ProfilePage', 'ProfilePage' in content)
        print('contains edge_owner_to_timeline_media', 'edge_owner_to_timeline_media' in content)
        print('has script count', len(await page.query_selector_all('script')))
        if 'ProfilePage' in content:
            idx = content.find('ProfilePage')
            print(content[idx-200:idx+400])
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
