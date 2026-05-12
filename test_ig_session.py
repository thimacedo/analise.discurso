
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

async def test_session():
    session_id = os.getenv("INSTAGRAM_SESSIONID")
    headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
    
    print(f"🚀 Iniciando teste de sessão headless...")
    print(f"🔑 SessionID: {session_id[:10]}...{session_id[-10:]}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Adiciona os cookies de sessão
        cookies_to_add = [
            {'name': 'sessionid', 'value': session_id, 'domain': '.instagram.com', 'path': '/'},
            {'name': 'ds_user_id', 'value': os.getenv("INSTAGRAM_DS_USER_ID", ""), 'domain': '.instagram.com', 'path': '/'},
            {'name': 'csrftoken', 'value': os.getenv("INSTAGRAM_CSRFTOKEN", ""), 'domain': '.instagram.com', 'path': '/'}
        ]
        await context.add_cookies([c for c in cookies_to_add if c['value']])
        
        page = await context.new_page()
        
        print("🌐 Acessando página inicial do Instagram...")
        await page.goto("https://www.instagram.com/", wait_until="networkidle", timeout=60000)
        await asyncio.sleep(5)
        
        cookies = await context.cookies()
        session_cookie = next((c for c in cookies if c['name'] == 'sessionid'), None)
        print(f"🍪 Cookie 'sessionid' presente após navegação? {'Sim' if session_cookie else 'Não'}")
        
        current_url = page.url
        print(f"📍 URL atual: {current_url}")
        
        content = await page.content()
        is_logged_in = os.getenv("IG_USER") in content or "Log Out" in content or "Sair" in content
        
        if is_logged_in:
            print("✅ SUCESSO: Sessão ativa (detectada por conteúdo)!")
        elif "accounts/login" in current_url:
            print("❌ FALHA: Sessão inválida (redirecionado para login).")
        else:
            print("⚠️ INDETERMINADO: Não parece logado, mas não redirecionou para login.")
            await page.screenshot(path="ig_debug_final.png")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_session())
