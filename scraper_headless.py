# scraper_headless.py
import sys
import asyncio
import logging
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logger = logging.getLogger("ScraperHeadless")

class InstagramScraperHeadless:
    def __init__(self, target_profile: str):
        self.target_profile = target_profile
        self.profile_url = f"https://www.instagram.com/{target_profile}/"

    async def fetch_recent_posts(self):
        logger.info(f"🚀 Iniciando Playwright Stealth para: {self.target_profile}")
        
        async with async_playwright() as p:
            # Lança o navegador com argumentos anti-detecção
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            
            # Cria um contexto de navegador (simula uma janela anônima com preferências)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080},
                locale='pt-BR'
            )
            
            page = await context.new_page()
            
            # Aplica o patch Stealth (esconde webdrivers, modifica fingerprints)
            await stealth_async(page)
            
            try:
                logger.info("🌐 Navegando para o perfil...")
                await page.goto(self.profile_url, wait_until="networkidle", timeout=30000)
                
                # Verifica se fomos redirecionados para a tela de login (o maior sinal de bloqueio)
                if "login" in page.url or "accounts/login" in page.url:
                    logger.error("❌ BLOQUEADO: Instagram redirecionou para a página de login!")
                    await page.screenshot(path="bloqueio_login.png")
                    return []

                # Espera o grid de posts aparecer (seletor de links de postagens)
                logger.info("⏳ Aguardando o grid de posts carregar...")
                await page.wait_for_selector('a[href*="/p/"]', timeout=15000)
                
                # Pequena pausa para garantir que o React carregou os elementos
                await asyncio.sleep(2)
                
                # Extrai todos os links de posts da página
                post_links = await page.eval_on_selector_all(
                    'a[href*="/p/"]',
                    'elements => elements.map(el => el.href)'
                )
                
                # Limpa e estrutura os dados
                posts = []
                seen = set()
                for link in post_links:
                    # O link vem no formato: https://www.instagram.com/p/SHORTCODE/
                    parts = link.split("/p/")
                    if len(parts) > 1:
                        shortcode = parts[1].split("/")[0]
                        if shortcode not in seen:
                            seen.add(shortcode)
                            posts.append({"shortcode": shortcode, "url": link})
                            
                logger.info(f"✅ SUCESSO! Extraídos {len(posts)} posts recentes do perfil {self.target_profile}.")
                return posts

            except Exception as e:
                logger.error(f"❌ Erro durante o scraping headless: {e}")
                # Tira print da tela no momento do erro para debugarmos
                await page.screenshot(path="erro_scraping.png")
                logger.info("📸 Print da tela salvo como erro_scraping.png")
                return []
            finally:
                await browser.close()

# Bloco de teste isolado
async def main():
    scraper = InstagramScraperHeadless("instagram") # Testando com o perfil oficial
    dados = await scraper.fetch_recent_posts()
    for d in dados[:5]: # Mostra os 5 primeiros
        print(d)

if __name__ == "__main__":
    asyncio.run(main())