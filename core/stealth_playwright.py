# core/stealth_playwright.py
import asyncio
import random
from playwright.async_api import async_playwright, BrowserContext, Page

class StealthBrowser:
    """Provedor de contexto de navegador com evasão de detecção (PASA v16.4)"""
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ]

    async def get_stealth_context(self, playwright, proxy: dict = None) -> BrowserContext:
        """Cria um contexto de navegador com injeções de camuflagem."""
        browser = await playwright.chromium.launch(headless=self.headless, proxy=proxy)
        context = await browser.new_context(
            user_agent=random.choice(self.user_agents),
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
        )
        
        # Injeção de scripts Stealth para remover sinalizadores de automação
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445) return 'Intel Inc.';
                if (parameter === 37446) return 'Intel(R) Iris(TM) Graphics 6100';
                return getParameter(parameter);
            };
        """)
        return context

    async def human_delay(self, min_ms: int = 500, max_ms: int = 2000):
        """Simula a hesitação humana com atraso gaussiano."""
        await asyncio.sleep(random.uniform(min_ms, max_ms) / 1000)
