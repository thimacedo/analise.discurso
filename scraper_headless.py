# scraper_headless.py
import sys
import asyncio
import logging
import os
from dotenv import load_dotenv
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger("ScraperHeadless")

load_dotenv()

class InstagramScraperHeadless:
    def __init__(self, target_profile: str):
        self.target_profile = target_profile
        self.profile_url = f"https://www.instagram.com/{target_profile}/"
        
        # Pegando as variáveis do .env com os nomes que você definiu
        self.session_id = os.getenv("INSTAGRAM_SESSIONID")
        self.ds_user_id = os.getenv("INSTAGRAM_DS_USER_ID")
        self.csrf_token = os.getenv("INSTAGRAM_CSRFTOKEN")

        if not self.session_id or not self.ds_user_id or not self.csrf_token:
            raise ValueError("❌ Variáveis de sessão do Instagram (INSTAGRAM_SESSIONID, etc) não encontradas no .env")

    async def fetch_recent_posts(self):
        logger.info(f"🚀 Iniciando Playwright com INJEÇÃO DE SESSÃO para: {self.target_profile}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080},
                locale='pt-BR'
            )
            
            # ==========================================
            # A MAGIA ACONTECE AQUI: INJEÇÃO DE COOKIES
            # ==========================================
            logger.info("🍪 Injetando cookies de sessão no navegador...")
            await context.add_cookies([
                {
                    "name": "sessionid",
                    "value": self.session_id,
                    "domain": ".instagram.com",
                    "path": "/",
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax"
                },
                {
                    "name": "ds_user_id",
                    "value": self.ds_user_id,
                    "domain": ".instagram.com",
                    "path": "/",
                    "secure": True
                },
                {
                    "name": "csrftoken",
                    "value": self.csrf_token,
                    "domain": ".instagram.com",
                    "path": "/",
                    "secure": True
                }
            ])
            
            page = await context.new_page()
            
            # Stealth Manual
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
            """)
            
            try:
                # NAVEGA DIRETO NO ALVO (sem passar pela tela de login)
                logger.info(f"🎯 Navegando direto para o perfil: {self.profile_url}")
                await page.goto(self.profile_url, wait_until="networkidle", timeout=30000)
                
                # Verifica se a injeção funcionou ou se fomos jogados na tela de login
                if "login" in page.url:
                    logger.error("❌ Fomos redirecionados para o Login. O SESSIONID pode ter expirado ou a conta foi bloqueada.")
                    await page.screenshot(path="falha_sessao.png")
                    return []

                # Tenta fechar aqueles pop-ups chatos de "Ativar Notificações" que aparecem logo que loga
                try:
                    await page.click('button:has-text("Agora não"), button:has-text("Not Now")', timeout=3000)
                    await asyncio.sleep(1)
                except Exception:
                    pass # Se não aparecer, segue o jogo

                # EXTRAÇÃO DOS DADOS
                logger.info("⏳ Aguardando o grid de posts carregar...")
                await page.wait_for_selector('a[href*="/p/"]', timeout=15000)
                
                await asyncio.sleep(2)
                
                post_links = await page.eval_on_selector_all(
                    'a[href*="/p/"]',
                    'elements => elements.map(el => el.href)'
                )
                
                posts = []
                seen = set()
                for link in post_links:
                    parts = link.split("/p/")
                    if len(parts) > 1:
                        shortcode = parts[1].split("/")[0]
                        if shortcode not in seen:
                            seen.add(shortcode)
                            posts.append({"shortcode": shortcode, "url": link})
                            
                logger.info(f"✅ SUCESSO! Extraídos {len(posts)} posts recentes.")
                return posts

            except Exception as e:
                logger.error(f"❌ Erro durante o scraping: {e}")
                await page.screenshot(path="erro_captura.png")
                logger.info("📸 Print salvo como erro_captura.png")
                return []
            finally:
                await browser.close()

async def main():
    # Usando um perfil real como teste
    scraper = InstagramScraperHeadless("instagram") 
    dados = await scraper.fetch_recent_posts()
    print(f"\n📝 Dados encontrados ({len(dados)} posts):")
    for d in dados[:5]: 
        print(d)

if __name__ == "__main__":
    asyncio.run(main())