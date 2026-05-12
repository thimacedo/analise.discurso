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
    def __init__(self, target_profile: str, max_posts: int = 5):
        self.target_profile = target_profile
        self.profile_url = f"https://www.instagram.com/{target_profile}/"
        self.max_posts = max_posts # Limite para não ficar horas raspando
        
        self.session_id = os.getenv("INSTAGRAM_SESSIONID")
        self.ds_user_id = os.getenv("INSTAGRAM_DS_USER_ID")
        self.csrf_token = os.getenv("INSTAGRAM_CSRFTOKEN")

        if not self.session_id or not self.ds_user_id or not self.csrf_token:
            raise ValueError("❌ Variáveis de sessão do Instagram não encontradas no .env")

    async def _inject_cookies(self, context):
        """Injeta os cookies de sessão para burlar o login."""
        await context.add_cookies([
            {"name": "sessionid", "value": self.session_id, "domain": ".instagram.com", "path": "/", "httpOnly": True, "secure": True, "sameSite": "Lax"},
            {"name": "ds_user_id", "value": self.ds_user_id, "domain": ".instagram.com", "path": "/", "secure": True},
            {"name": "csrftoken", "value": self.csrf_token, "domain": ".instagram.com", "path": "/", "secure": True}
        ])

    async def _extract_post_data(self, page, shortcode: str) -> dict:
        """Navega para a página do post e extrai Legenda e Data."""
        post_url = f"https://www.instagram.com/p/{shortcode}/" if "/p/" in shortcode else f"https://www.instagram.com/reel/{shortcode}/"
        
        try:
            await page.goto(post_url, wait_until="domcontentloaded", timeout=20000)
            
            # Espera o corpo do post carregar
            await page.wait_for_selector('time', timeout=10000)
            
            # Extrai a Data
            time_element = await page.query_selector('time')
            date_str = await time_element.get_attribute('datetime') if time_element else "Unknown"
            
            # Extrai a Legenda (Texto)
            # O Instagram guarda o texto dentro de um <h1> no modal do post, ou no span do feed
            caption = ""
            h1_element = await page.query_selector('h1')
            if h1_element:
                caption = await h1_element.inner_text()
            else:
                # Fallback para reels ou layout diferente
                span_element = await page.query_selector('article div[role="button"] span')
                if span_element:
                    caption = await span_element.inner_text()

            # Delay humano para evitar bloqueio por comportamento robótico
            await asyncio.sleep(2) 
            
            return {
                "shortcode": shortcode,
                "text": caption.strip(),
                "timestamp": date_str
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Não foi possível extrair dados do post {shortcode}: {e}")
            return {"shortcode": shortcode, "text": "", "timestamp": "Error"}

    async def fetch_recent_posts(self):
        logger.info(f"🚀 Iniciando Playwright para: {self.target_profile}")
        
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
            
            await self._inject_cookies(context)
            
            page = await context.new_page()
            
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
            """)
            
            try:
                # 1. Acessa o Perfil
                logger.info(f"🎯 Navegando para o perfil: {self.profile_url}")
                await page.goto(self.profile_url, wait_until="domcontentloaded", timeout=30000)
                
                if "login" in page.url:
                    logger.error("❌ Sessão expirada. Fomos redirecionados para o Login.")
                    return []

                # Tenta fechar pop-ups
                try:
                    await page.click('button:has-text("Agora não"), button:has-text("Not Now")', timeout=2000)
                except Exception:
                    pass

                # 2. Lista os Shortcodes
                logger.info("⏳ Aguardando o grid carregar...")
                selector = 'a[href*="/p/"], a[href*="/reel/"]'
                await page.wait_for_selector(selector, timeout=15000)
                await asyncio.sleep(2)
                
                post_links = await page.eval_on_selector_all(selector, 'elements => elements.map(el => el.href)')
                
                shortcodes = []
                seen = set()
                for link in post_links:
                    parts = link.split("/")
                    for i, part in enumerate(parts):
                        if part in ("p", "reel") and i + 1 < len(parts):
                            sc = parts[i+1]
                            if sc not in seen:
                                seen.add(sc)
                                shortcodes.append(sc)
                
                # Limita a quantidade para o teste
                shortcodes = shortcodes[:self.max_posts]
                logger.info(f"✅ Encontrados {len(shortcodes)} posts. Iniciando extração profunda...")

                # 3. Extração Profunda (Legenda e Data)
                detailed_posts = []
                for index, sc in enumerate(shortcodes):
                    logger.info(f"🔍 Extraindo [{index+1}/{len(shortcodes)}]: {sc}")
                    post_data = await self._extract_post_data(page, sc)
                    detailed_posts.append(post_data)
                    
                return detailed_posts

            except Exception as e:
                logger.error(f"❌ Erro geral: {e}")
                await page.screenshot(path="erro_geral.png")
                return []
            finally:
                await browser.close()

async def main():
    # Testando com o perfil do Instagram (mude para o alvo político de vocês depois)
    scraper = InstagramScraperHeadless("instagram", max_posts=3) 
    dados = await scraper.fetch_recent_posts()
    
    print("\n" + "="*50)
    print("📝 DADOS EXTRAÍDOS PARA ANÁLISE PASA:")
    print("="*50)
    for d in dados: 
        print(f"📅 Data: {d.get('timestamp')}")
        print(f"🔗 Shortcode: {d.get('shortcode')}")
        print(f"💬 Texto: {d.get('text')[:150]}...") # Limita a 150 chars pra não poluir o terminal
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())