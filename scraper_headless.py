# scraper_headless.py
import sys
import asyncio
import logging
import os
import json
from typing import Any
from dotenv import load_dotenv
from playwright.async_api import async_playwright

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger("ScraperHeadless")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()

class InstagramScraperHeadless:
    def __init__(self, target_profile: str, max_posts: int = 5):
        self.target_profile = target_profile
        self.profile_url = f"https://www.instagram.com/{target_profile}/"
        self.max_posts = max_posts 
        
        self.session_id = os.getenv("INSTAGRAM_SESSIONID")
        self.session_id_fallback = os.getenv("INSTAGRAM_SESSIONID_FALLBACK")
        self.ds_user_id = os.getenv("INSTAGRAM_DS_USER_ID")
        self.csrf_token = os.getenv("INSTAGRAM_CSRFTOKEN")

        if not self.session_id and not self.session_id_fallback:
            raise ValueError("❌ Nenhuma variável de sessão do Instagram (principal ou fallback) encontrada no .env")

    async def _inject_cookies(self, context, session_id=None):
        sid = session_id or self.session_id or self.session_id_fallback
        await context.add_cookies([
            {"name": "sessionid", "value": sid, "domain": ".instagram.com", "path": "/", "httpOnly": True, "secure": True, "sameSite": "Lax"},
            {"name": "ds_user_id", "value": self.ds_user_id, "domain": ".instagram.com", "path": "/", "secure": True},
            {"name": "csrftoken", "value": self.csrf_token, "domain": ".instagram.com", "path": "/", "secure": True}
        ])

    async def fetch_recent_posts(self, external_cookies: Any = None):
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
            
            if external_cookies:
                logger.info("🔑 Preparando injeção de cookies externos...")
                try:
                    cookies_to_inject = []
                    
                    # Caso 1: Recebeu uma string (pode ser JSON ou ID puro)
                    if isinstance(external_cookies, str):
                        try:
                            parsed = json.loads(external_cookies)
                            if isinstance(parsed, list):
                                cookies_to_inject = parsed
                            elif isinstance(parsed, dict):
                                cookies_to_inject = [parsed]
                            else:
                                # Se decodificou mas não é lista/dict (ex: "ID_PURO"), trata como string
                                raise ValueError("JSON decodificado não é objeto/lista")
                        except (json.JSONDecodeError, ValueError):
                            logger.info("⚠️ Cookies em formato string simples. Montando objeto...")
                            cookies_to_inject = [
                                {"name": "sessionid", "value": external_cookies.strip('"'), "domain": ".instagram.com", "path": "/", "httpOnly": True, "secure": True, "sameSite": "Lax"},
                                {"name": "ds_user_id", "value": self.ds_user_id, "domain": ".instagram.com", "path": "/", "secure": True},
                                {"name": "csrftoken", "value": self.csrf_token, "domain": ".instagram.com", "path": "/", "secure": True}
                            ]
                    
                    # Caso 2: Já recebeu uma lista
                    elif isinstance(external_cookies, list):
                        cookies_to_inject = external_cookies
                    
                    # Caso 3: Já recebeu um dict único
                    elif isinstance(external_cookies, dict):
                        cookies_to_inject = [external_cookies]

                    # Validação Final e Injeção
                    if isinstance(cookies_to_inject, list) and len(cookies_to_inject) > 0:
                        logger.info(f"✅ Injetando {len(cookies_to_inject)} cookies no contexto.")
                        await context.add_cookies(cookies_to_inject)
                    else:
                        logger.warning("❓ Nenhum cookie válido extraído. Usando fallback.")
                        await self._inject_cookies(context)
                except Exception as e:
                    logger.error(f"❌ Falha crítica ao injetar cookies: {e}")
                    await self._inject_cookies(context)
            else:
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
                await page.goto(self.profile_url, wait_until="load", timeout=60000)
                
                # Aguarda um pouco para JS carregar
                await asyncio.sleep(5)
                
                logger.info(f"📄 Página carregada: {await page.title()} | URL Atual: {page.url}")

                if "login" in page.url:
                    logger.error("❌ Sessão expirada ou bloqueio de login.")
                    return []

                # Tenta fechar pop-ups
                try:
                    await page.click('button:has-text("Agora não"), button:has-text("Not Now")', timeout=3000)
                except Exception:
                    pass

                # Pequeno scroll para "acordar" o carregamento dinâmico
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(2)

                # 2. Captura os elementos dos posts (não os links, mas os objetos clicáveis)
                logger.info("⏳ Aguardando o grid carregar...")
                selector = 'a[href*="/p/"], a[href*="/reel/"]'
                
                try:
                    await page.wait_for_selector(selector, timeout=30000)
                except Exception:
                    logger.warning("⚠️ Grid de posts não encontrado no tempo limite. Tentando captura direta.")
                
                post_elements = await page.query_selector_all(selector)
                
                if not post_elements:
                    logger.error(f"❌ Nenhum post encontrado para @{self.target_profile}. Perfil privado ou bloqueio?")
                    await page.screenshot(path=f"falha_{self.target_profile}.png")
                    return []

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

                        # --- NOVO: Extração de Comentários ---
                        comments = []
                        # Seletores comuns para texto de comentário no Instagram
                        comment_selectors = [
                            'div[role="dialog"] ul div[role="menuitem"] span[dir="auto"]',
                            'div[role="dialog"] ul li span'
                        ]
                        
                        for selector_cmd in comment_selectors:
                            elements = await page.query_selector_all(selector_cmd)
                            for el in elements:
                                text_cmd = await el.inner_text()
                                # Filtra a legenda (geralmente é o primeiro) e textos curtos
                                if text_cmd and text_cmd != caption and len(text_cmd) > 2:
                                    comments.append({
                                        "text": text_cmd,
                                        "ownerUsername": "unknown", # Playwright extrai texto puro aqui
                                        "timestamp": datetime.now(timezone.utc).isoformat()
                                    })
                                if len(comments) >= 10: break # Limite por post
                            if comments: break

                        detailed_posts.append({
                            "shortcode": shortcode,
                            "text": caption.strip(),
                            "timestamp": date_str,
                            "comments": comments
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
    scraper = InstagramScraperHeadless("cironogueira", max_posts=3) 
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
