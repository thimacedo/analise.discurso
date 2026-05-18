import scrapy
import re
import asyncio
import json
from scrapy_playwright.page import PageMethod
from ..items import InstagramCommentItem

class InstagramDOMSpider(scrapy.Spider):
    """
    Tier 2 (Fallback): Renderização visual via Playwright.
    Vantagens: Funciona mesmo se a API mudar.
    Desvantagens: Lento, usa mais memória, risco de OOM.
    """
    name = 'instagram_dom'
    
    custom_settings = {
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        'TWISTED_REACTOR': "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'timeout': 30000,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',  # Evita OOM
                '--disable-gpu',
            ]
        },
        'PLAYWRIGHT_MAX_PAGES_PER_CONTEXT': 3,  # Limita páginas abertas
        'ITEM_PIPELINES': {
           'sentinela_scrapy.pipelines.QualityGatePipeline': 300,
           'sentinela_scrapy.pipelines.CleanCommentPipeline': 350,
        }
    }
    
    def __init__(self, username='', sessionid='', max_posts=5, max_comments=50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.sessionid = sessionid
        self.max_posts = int(max_posts)
        self.max_comments = int(max_comments)
        
    def start_requests(self):
        url = f"https://www.instagram.com/{self.username}/"
        
        yield scrapy.Request(
            url=url,
            callback=self.parse_profile,
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_load_state", "networkidle"),
                    PageMethod("wait_for_timeout", 3000),
                ],
                "tier": 2
            },
            cookies={"sessionid": self.sessionid},
            errback=self.errback_close_page,
            dont_filter=True
        )
        
    async def parse_profile(self, response):
        """Extrai links dos posts do perfil."""
        page = response.meta.get("playwright_page")
        if not page:
            return
            
        try:
            # Espera o grid carregar
            try:
                await page.wait_for_selector('a[href*="/p/"], a[href*="/reel/"]', timeout=15000)
            except Exception:
                self.logger.error("❌ Tier 2: Grid de posts não encontrado. Possível Login Wall.")
                await page.close()
                return
                
            # Extrai links dos posts (limitado por max_posts)
            links = await page.evaluate(f"""() => {{
                const anchors = Array.from(document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]'));
                return anchors.map(a => a.href).slice(0, {self.max_posts});
            }}""")
            
            self.logger.info(f"✅ Tier 2: Encontrados {len(links)} posts no perfil @{self.username}")
            
            for link in links:
                yield scrapy.Request(
                    url=link,
                    callback=self.parse_post,
                    meta={
                        "playwright": True,
                        "playwright_include_page": True,
                        "playwright_page_methods": [
                            PageMethod("wait_for_load_state", "networkidle"),
                            PageMethod("wait_for_timeout", 2000),
                        ],
                        "tier": 2
                    },
                    cookies={"sessionid": self.sessionid},
                    errback=self.errback_close_page,
                    dont_filter=True
                )
        finally:
            await page.close()
            
    async def parse_post(self, response):
        """Extrai comentários de um post."""
        page = response.meta.get("playwright_page")
        if not page:
            return
            
        shortcode_match = re.search(r'/(?:p|reel)/([^/?#&]+)', response.url)
        shortcode = shortcode_match.group(1) if shortcode_match else "unknown"
        
        try:
            # Scroll e clique no "Carregar mais" com timeout
            comments_loaded = 0
            max_attempts = self.max_comments // 12  # Instagram carrega ~12 por vez
            
            for attempt in range(max_attempts):
                try:
                    # Tentativas múltiplas de seletores (Instagram muda isso)
                    load_more = None
                    selectors = [
                        'button svg[aria-label*="Carregar"]',
                        'button:has-text("more comments")',
                        'button:has-text("Ver mais")',
                        'button span:has-text("View")',
                    ]
                    
                    for selector in selectors:
                        load_more = await page.query_selector(selector)
                        if load_more:
                            break
                    
                    if load_more:
                        await load_more.click()
                        await page.wait_for_timeout(1500)
                        comments_loaded += 12
                    else:
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Tier 2: Não há mais comentários para carregar ({e})")
                    break
            
            # Extração: Primeiro tenta JSON embutido, depois DOM
            content = await page.content()
            
            # Método 1: JSON embutido
            json_match = re.search(r'window\._sharedData\s*=\s*({.*?});', content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(1))
                    comments = self._extract_from_json(data, shortcode)
                    if comments:
                        for comment in comments:
                            yield comment
                        self.logger.info(f"✅ Tier 2 (JSON): {len(comments)} comentários extraídos de {shortcode}")
                        return
                except Exception as e:
                    self.logger.debug(f"Tier 2: JSON parsing falhou, tentando DOM: {e}")
            
            # Método 2: DOM (fallback)
            comment_blocks = await page.query_selector_all('ul ul li, li[role="menuitem"]')
            dom_comments = []
            
            for block in comment_blocks[:self.max_comments]:
                try:
                    username_el = await block.query_selector('a[role="link"] span, h3 a span')
                    username = (await username_el.inner_text()).strip() if username_el else "unknown"
                    
                    text_els = await block.query_selector_all('span[dir="auto"]')
                    text = " ".join([await el.inner_text() for el in text_els]).strip()
                    
                    if text and len(text) > 2 and username != "unknown":
                        dom_comments.append(InstagramCommentItem(
                            comment_id=f"dom_{hash(text + username)}",
                            post_shortcode=shortcode,
                            ownerUsername=username,
                            text=text,
                            candidato_id=self.username,
                            tier_used=2
                        ))
                except Exception as e:
                    continue
            
            for comment in dom_comments:
                yield comment
                
            self.logger.info(f"✅ Tier 2 (DOM): {len(dom_comments)} comentários extraídos de {shortcode}")
                    
        finally:
            await page.close()
    
    def _extract_from_json(self, data, shortcode):
        """Extrai comentários do JSON embutido."""
        comments = []
        try:
            for key, val in data.items():
                if isinstance(val, dict) and 'graphql' in val:
                    edges = val.get('graphql', {}).get('shortcode_media', {}).get('edge_media_to_parent_comment', {}).get('edges', [])
                    for edge in edges:
                        node = edge.get('node', {})
                        comments.append(InstagramCommentItem(
                            comment_id=node.get("id"),
                            post_shortcode=shortcode,
                            ownerUsername=node.get("owner", {}).get("username"),
                            text=node.get("text"),
                            candidato_id=self.username,
                            tier_used=2
                        ))
        except Exception:
            pass
        return comments

    async def errback_close_page(self, failure):
        """Fecha página em caso de erro."""
        page = failure.request.meta.get("playwright_page")
        if page:
            await page.close()
        self.logger.error(f"❌ Tier 2: Erro na requisição: {failure.request.url}")
