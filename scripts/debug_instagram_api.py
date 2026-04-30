import asyncio
from playwright.async_api import async_playwright

PROFILE = 'edinhosilvapt'

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f'https://www.instagram.com/{PROFILE}/', wait_until='networkidle', timeout=30000)
        result = await page.evaluate(r"""
            async () => {
                try {
                    const response = await fetch(`/api/v1/users/web_profile_info/?username=${window.location.pathname.slice(1)}`);
                    const text = await response.text();
                    return {
                        status: response.status,
                        ok: response.ok,
                        body_snippet: text.slice(0, 2000)
                    };
                } catch (e) {
                    return {error: e.toString()};
                }
            }
        """)
        print(result)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
