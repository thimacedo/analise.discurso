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
        self.max_posts = max_posts 
        
        self.session_id = os.getenv("INSTAGRAM_SESSIONID")
        self.ds_user_id = os.getenv("INSTAGRAM_DS_USER_ID")
        self.csrf_token = os.getenv("INSTAGRAM_CSRFTOKEN")

        if not self.session_id or not self.ds_user_id or not self.csrf_token:
            raise ValueError("❌ Variáveis de sessão do Instagram não encontradas no .env")

    async def _inject_cookies(self, context):
        await context.add_cookies([
            {"name": "sessionid", "value": self.session_id, "domain": ".instagram.com", "path": "/", "httpOnly": True, "secure": True, "sameSite": "Lax"},
            {"name": "ds_user_id", "value": self.ds_user_id, "domain": ".instagram.com", "path": "/", "secure": True},
            {"name": "csrftoken", "value": self.csrf_token, "domain": ".instagram.com", "path": "/", "secure": True}
        ])

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
                    logger.error("❌ Sessão expirada.")
                    return []

                # Tenta fechar pop-ups
                try:
                    await page.click('button:has-text("Agora não"), button:has-text("Not Now")', timeout=2000)
                except Exception:
                    pass

                # 2. Captura os elementos dos posts (não os links, mas os objetos clicáveis)
                logger.info("⏳ Aguardando o grid carregar...")
                selector = 'a[href*="/p/"], a[href*="/reel/"]'
                await page.wait_for_selector(selector, timeout=15000)
                await asyncio.sleep(2)
                
                post_elements = await page.query_selector_all(selector)
                
                # Limita a quantidade
                post_elements = post_elements[:self.max_posts]
                logger.info(f"✅ Encontrados {len(post_elements)} posts. Extraindo via Modal...")

                detailed_posts = []
                
                # 3. Extração via Modal (Clicando no Post)
                for index, element in enumerate(post_elements):
                    try:
                        logger.info(f"🔍 Abrindo post [{index+1}/{len(post_elements)}] via Modal...")
                        
                        # Pega o shortcode antes de clicar
                        href = await element.get_attribute('href')
                        shortcode = href.strip('/').split('/')[-1]
                        
                        # Clica no post para abrir o modal
                        await element.click()
                        
                        # Espera o modal carregar (o modal é um div com role="dialog")
                        await page.wait_for_selector('div[role="dialog"]', timeout=10000)
                        await asyncio.sleep(1) # Pausa para o React renderizar a legenda
                        
                        # Extrai a Data (procura a tag <time> dentro do modal)
                        time_element = await page.query_selector('div[role="dialog"] time')
                        date_str = await time_element.get_attribute('datetime') if time_element else "Unknown"
                        
                        # Extrai a Legenda
                        caption = ""
                        # A legenda no modal costuma estar no primeiro <h1> ou em um span longo
                        h1_element = await page.query_selector('div[role="dialog"] h1')
                        if h1_element:
                            caption = await h1_element.inner_text()
                        else:
                            # Fallback para reels que usam span
                            span_element = await page.query_selector('div[role="dialog"] div > span')
                            if span_element:
                                caption = await span_element.inner_text()

                        detailed_posts.append({
                            "shortcode": shortcode,
                            "text": caption.strip(),
                            "timestamp": date_str
                        })
                        
                        # Fecha o modal usando a tecla Escape (muito mais limpo que clicar no X)
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(2) # Delay humano para o modal fechar e a página estabilizar

                    except Exception as e:
                        logger.warning(f"⚠️ Erro ao processar post {index+1}: {e}")
                        # Se der erro, tenta fechar o modal e continuar para o próximo
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(2)
                    
                return detailed_posts

            except Exception as e:
                logger.error(f"❌ Erro geral: {e}")
                await page.screenshot(path="erro_geral.png")
                return []
            finally:
                await browser.close()

async def main():
    scraper = InstagramScraperHeadless("instagram", max_posts=3) 
    dados = await scraper.fetch_recent_posts()
    
    print("\n" + "="*50)
    print("📝 DADOS EXTRAÍDOS PARA ANÁLISE PASA:")
    print("="*50)
    for d in dados: 
        print(f"📅 Data: {d.get('timestamp')}")
        print(f"🔗 Shortcode: {d.get('shortcode')}")
        print(f"💬 Texto: {d.get('text')[:200]}...") 
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
