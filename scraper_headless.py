# scraper_headless.py
import sys
import asyncio
import logging
import os
import json
from datetime import datetime, timezone
from typing import Any, List, Dict, Optional
from dotenv import load_dotenv
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger("ScraperHeadless")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()

class InstagramScraperHeadless:
    def __init__(self, target_profile: str, max_posts: int = 5, max_comments: int = 20):
        self.target_profile = target_profile
        self.profile_url = f"https://www.instagram.com/{target_profile}/"
        self.max_posts = max_posts 
        self.max_comments = max_comments
        
        self.session_id = os.getenv("INSTAGRAM_SESSIONID")
        self.session_id_fallback = os.getenv("INSTAGRAM_SESSIONID_FALLBACK")
        self.ds_user_id = os.getenv("INSTAGRAM_DS_USER_ID")
        self.csrf_token = os.getenv("INSTAGRAM_CSRFTOKEN")

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def _launch_browser(self, headless: bool = True):
        if not self.playwright:
            self.playwright = await async_playwright().start()
        
        if not self.browser:
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            
        if not self.context:
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080},
                locale='pt-BR'
            )
            
        if not self.page:
            self.page = await self.context.new_page()
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
            """)

    async def close(self):
        try:
            if self.page: await self.page.close()
            if self.context: await self.context.close()
            if self.browser: await self.browser.close()
            if self.playwright: await self.playwright.stop()
        except Exception:
            pass
        self.page = self.context = self.browser = self.playwright = None

    async def _is_profile_not_found(self):
        try:
            # Verifica mensagens comuns de erro do Instagram
            return await self.page.locator('text="Esta página não está disponível", text="Page not found"').count() > 0
        except Exception:
            return False

    async def _extract_post_links(self):
        try:
            selector = 'a[href*="/p/"], a[href*="/reel/"]'
            await self.page.wait_for_selector(selector, timeout=15000)
            elements = await self.page.query_selector_all(selector)
            links = []
            for el in elements:
                href = await el.get_attribute("href")
                if href and href not in links:
                    links.append(href)
            return links
        except Exception:
            return []

    async def _inject_cookies(self, external_cookies: Any):
        if not external_cookies:
            sid = self.session_id or self.session_id_fallback
            if sid:
                await self.context.add_cookies([
                    {"name": "sessionid", "value": sid, "domain": ".instagram.com", "path": "/", "httpOnly": True, "secure": True, "sameSite": "Lax"}
                ])
                return True
            return False

        try:
            cookies_to_inject = []
            if isinstance(external_cookies, str):
                try:
                    parsed = json.loads(external_cookies)
                    cookies_to_inject = parsed if isinstance(parsed, list) else [parsed]
                except Exception:
                    cookies_to_inject = [{"name": "sessionid", "value": external_cookies.strip('"'), "domain": ".instagram.com", "path": "/", "httpOnly": True, "secure": True, "sameSite": "Lax"}]
            elif isinstance(external_cookies, list):
                cookies_to_inject = external_cookies
            elif isinstance(external_cookies, dict):
                cookies_to_inject = [external_cookies]

            if cookies_to_inject:
                await self.context.add_cookies(cookies_to_inject)
                return True
        except Exception as e:
            logger.error(f"❌ Erro ao injetar cookies: {e}")
        return False

    async def fetch_recent_posts(self, external_cookies: Any = None, retry_count: int = 0) -> List[Dict[str, Any]]:
        logger.info(f"🚀 Iniciando Playwright para: {self.target_profile} (Tentativa {retry_count + 1})")

        try:
            await self._launch_browser(headless=True)

            if external_cookies:
                await self._inject_cookies(external_cookies)
            else:
                await self._inject_cookies(None)

            profile_url = f"https://www.instagram.com/{self.target_profile}/"
            await self.page.goto(profile_url, wait_until="networkidle", timeout=45000)
            await asyncio.sleep(3)

            # Detecção Rápida de Login Wall
            current_url = self.page.url
            if "/accounts/login/" in current_url or await self.page.locator('input[name="username"]').count() > 0:
                logger.error("❌ Login Wall detectado. Sessão provavelmente expirada.")
                return [] 

            if await self._is_profile_not_found():
                logger.error(f"❌ Perfil @{self.target_profile} não encontrado.")
                return []

            # Tenta encontrar posts no grid
            post_links = await self._extract_post_links()
            if not post_links:
                # AUTOCURA: Se não achou posts e é a 1ª tentativa, reinicia o navegador
                if retry_count == 0:
                    logger.warning("⚠️ Grid vazio. Chrome pode ter crashado ou bloqueado. Reiniciando navegador internamente...")
                    await self.close()
                    await asyncio.sleep(3)
                    return await self.fetch_recent_posts(external_cookies, retry_count=1)
                else:
                    logger.warning(f"⚠️ Nenhum post encontrado após reinício do navegador para @{self.target_profile}.")
                    return []

            logger.info(f"✅ Encontrados {len(post_links)} posts. Iniciando extração...")
            
            detailed_posts = []
            # Obtém os elementos novamente para clicar
            selector = 'a[href*="/p/"], a[href*="/reel/"]'
            post_elements = await self.page.query_selector_all(selector)
            
            for index, element in enumerate(post_elements[:self.max_posts]):
                try:
                    logger.info(f"🔍 Abrindo post [{index+1}/{min(len(post_elements), self.max_posts)}]...")
                    
                    href = await element.get_attribute('href')
                    shortcode = href.strip('/').split('/')[-1]
                    
                    await element.click()
                    await self.page.wait_for_selector('div[role="dialog"]', timeout=10000)
                    await asyncio.sleep(2)
                    
                    # Extração de Data
                    time_element = await self.page.query_selector('div[role="dialog"] time')
                    date_str = await time_element.get_attribute('datetime') if time_element else datetime.now(timezone.utc).isoformat()
                    
                    # Extração de Legenda
                    caption = ""
                    h1_element = await self.page.query_selector('div[role="dialog"] h1')
                    if h1_element:
                        caption = await h1_element.inner_text()
                    else:
                        span_element = await self.page.query_selector('div[role="dialog"] div > span')
                        if span_element:
                            caption = await span_element.inner_text()

                    # Extração de Comentários
                    comments = []
                    comment_selectors = [
                        'div[role="dialog"] ul div[role="menuitem"] span[dir="auto"]',
                        'div[role="dialog"] ul li span'
                    ]
                    
                    for sel in comment_selectors:
                        els = await self.page.query_selector_all(sel)
                        for el in els:
                            t = await el.inner_text()
                            if t and t != caption and len(t) > 2:
                                comments.append({
                                    "text": t,
                                    "ownerUsername": "unknown",
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                })
                            if len(comments) >= self.max_comments: break
                        if comments: break

                    detailed_posts.append({
                        "shortcode": shortcode,
                        "text": caption.strip(),
                        "timestamp": date_str,
                        "comments": comments
                    })
                    
                    await self.page.keyboard.press('Escape')
                    await asyncio.sleep(2)

                except Exception as e:
                    logger.warning(f"⚠️ Erro ao processar post {index+1}: {e}")
                    await self.page.keyboard.press('Escape')
                    await asyncio.sleep(2)

            return detailed_posts

        except Exception as e:
            # AUTOCURA: Reinicia se o navegador fechou inesperadamente
            if "browser has been closed" in str(e).lower() or "target closed" in str(e).lower():
                if retry_count == 0:
                    logger.warning(f"💥 Chrome crashou durante execução. Tentando reiniciar internamente...")
                    await self.close()
                    await asyncio.sleep(5)
                    return await self.fetch_recent_posts(external_cookies, retry_count=1)
            
            logger.error(f"💥 Erro irrecuperável na raspagem: {e}")
            return []
        finally:
            await self.close()

async def main():
    scraper = InstagramScraperHeadless("cironogueira", max_posts=2) 
    dados = await scraper.fetch_recent_posts()
    
    print("\n" + "="*50)
    print("📝 DADOS EXTRAÍDOS PARA ANÁLISE PASA:")
    print("="*50)
    for d in dados: 
        print(f"📅 Data: {d.get('timestamp')}")
        print(f"🔗 Shortcode: {d.get('shortcode')}")
        print(f"💬 Comentários: {len(d.get('comments', []))}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
