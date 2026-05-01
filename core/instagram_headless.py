import os
import re
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Optional, Dict
from dotenv import load_dotenv
from supabase import create_client
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
IG_USER = os.getenv("IG_USER")
IG_PASS = os.getenv("IG_PASS")
INSTAGRAM_SESSIONID = os.getenv("INSTAGRAM_SESSIONID")
INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID")
INSTAGRAM_CSRF = os.getenv("INSTAGRAM_CSRF")
INSTAGRAM_DID = os.getenv("INSTAGRAM_DID")
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
MAX_POSTS_PER_PROFILE = int(os.getenv("MAX_POSTS_PER_PROFILE", "3"))
MAX_COMMENTS_PER_POST = int(os.getenv("MAX_COMMENTS_PER_POST", "50"))
INSTAGRAM_LOGIN_URL = "https://www.instagram.com/accounts/login/"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class InstagramHeadlessScraper:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def run(self, limit: int = 15):
        print("🧠 [Headless] Iniciando Instagram Headless Scraper...")

        async with async_playwright() as pw:
            self.playwright = pw
            self.browser = await pw.chromium.launch(
                headless=PLAYWRIGHT_HEADLESS,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                locale="pt-BR",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                ),
                extra_http_headers={
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                },
            )

            await context.add_init_script(
                "() => { Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); }"
            )

            if INSTAGRAM_SESSIONID:
                cookies = [
                    {
                        "name": "sessionid",
                        "value": INSTAGRAM_SESSIONID,
                        "domain": ".instagram.com",
                        "path": "/",
                    }
                ]
                if INSTAGRAM_USER_ID:
                    cookies.append({"name": "ds_user_id", "value": INSTAGRAM_USER_ID, "domain": ".instagram.com", "path": "/"})
                if INSTAGRAM_CSRF:
                    cookies.append({"name": "csrftoken", "value": INSTAGRAM_CSRF, "domain": ".instagram.com", "path": "/"})
                if INSTAGRAM_DID:
                    cookies.append({"name": "ig_did", "value": INSTAGRAM_DID, "domain": ".instagram.com", "path": "/"})
                
                await context.add_cookies(cookies)

            self.page = await context.new_page()
            self.page.set_default_timeout(60000) # 60 segundos
            
            logged = await self._ensure_logged_in()
            if not logged:
                print("❌ [Headless] Falha ao autenticar no Instagram. Abortando.")
                return

            targets = self._load_pending_targets(limit)
            if not targets:
                print("✅ [Headless] Nenhum perfil pendente para raspagem.")
                return

            for candidate in targets:
                await self._scrape_candidate(candidate)

            await self.page.close()
            await context.close()
            await self.browser.close()

    def _load_pending_targets(self, limit: int) -> List[Dict]:
        try:
            response = supabase.table('candidatos').select('id,username').is_('last_scraped_at', 'null').limit(limit).execute()
            return response.data or []
        except Exception as e:
            print(f"❌ [Headless] Erro ao buscar alvos pendentes: {e}")
            return []

    async def _ensure_logged_in(self) -> bool:
        assert self.page is not None

        try:
            # Tenta carregar a home do Instagram. Se os cookies funcionarem, seremos redirecionados ou veremos o feed.
            print("🌐 [Headless] Acessando Instagram home...")
            await self.page.goto("https://www.instagram.com/", wait_until="commit")
            await asyncio.sleep(10) # Aguarda renderização

            current_url = self.page.url
            print(f"📍 [Headless] URL atual: {current_url}")

            if "/accounts/login/" not in current_url:
                print("✅ [Headless] Autenticação confirmada (não redirecionado para login).")
                return True
            
            # Se cair aqui, tenta o fluxo de login tradicional
            print("🔑 [Headless] Cookies falharam. Tentando login tradicional...")
            await self.page.goto(INSTAGRAM_LOGIN_URL, wait_until="domcontentloaded")
            await asyncio.sleep(5)

            username_selector = 'input[name="username"], input[name="email"]'
            password_selector = 'input[name="password"], input[name="pass"]'
            username_count = await self.page.locator(username_selector).count()
            password_count = await self.page.locator(password_selector).count()
            has_username = username_count > 0
            has_password = password_count > 0

            if has_username and has_password:
                if not IG_USER or not IG_PASS:
                    print("❌ [Headless] Não há credenciais IG_USER/IG_PASS para login.")
                    return False

                print("🔑 [Headless] Login via Playwright...")
                if await self.page.locator('input[name="email"]').count() > 0:
                    await self.page.fill('input[name="email"]', IG_USER)
                else:
                    await self.page.fill('input[name="username"]', IG_USER)

                await self.page.fill(password_selector, IG_PASS)
                await asyncio.sleep(1)
                if await self.page.locator('button[type="submit"]').count() > 0:
                    await self.page.click('button[type="submit"]')
                else:
                    await self.page.locator(password_selector).press('Enter')
                await self.page.wait_for_load_state("networkidle", timeout=30000)
                await asyncio.sleep(5)

                if await self._has_session_cookie():
                    print("✅ [Headless] Login realizado com sucesso.")
                    return True

                print("❌ [Headless] Login não foi possível. Verifique credenciais ou 2FA.")
                return False

            print("⚠️ [Headless] Não foi possível detectar o formulário de login. Tentando seguir com a sessão atual.")
            return await self._has_session_cookie()
        except PlaywrightTimeoutError:
            print("❌ [Headless] Timeout durante autenticação no Instagram.")
            return False
        except Exception as e:
            print(f"❌ [Headless] Erro durante autenticação: {e}")
            return False

    async def _has_session_cookie(self) -> bool:
        assert self.page is not None
        cookies = await self.page.context.cookies()
        return any(cookie.get('name') == 'sessionid' and cookie.get('value') for cookie in cookies)

    async def _scrape_candidate(self, candidate: Dict):
        username = candidate.get('username')
        candidate_id = candidate.get('id')
        if not username:
            return

        print(f"\n🎯 [Headless] Raspando @{username}...")
        profile_url = f"https://www.instagram.com/{username}/"

        try:
            await self.page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(10) # Aumentado para garantir carregamento

            # Tenta fechar modais/popups que bloqueiam a visão
            try:
                close_btn = await self.page.query_selector('div[role="dialog"] button, button:has-text("Agora não"), button:has-text("Not Now")')
                if close_btn:
                    await close_btn.click()
                    await asyncio.sleep(2)
            except: pass

            # Scroll proativo para disparar renderização de posts
            await self.page.mouse.wheel(0, 500)
            await asyncio.sleep(3)

            # Tenta extrair seguidores via DOM com múltiplos seletores
            followers = 0
            followers_selectors = [
                'header section ul li:nth-child(2) span',
                'span[title]',
                'a[href$="/followers/"] span'
            ]
            
            for selector in followers_selectors:
                try:
                    el = await self.page.query_selector(selector)
                    if el:
                        text = await el.get_attribute('title') or await el.inner_text()
                        if text:
                            clean_f = re.sub(r'[^\d,KkMm]', '', text.replace('.', '').replace(' ', ''))
                            if 'M' in clean_f.upper():
                                followers = int(float(clean_f.upper().replace('M', '').replace(',', '.')) * 1_000_000)
                            elif 'K' in clean_f.upper():
                                followers = int(float(clean_f.upper().replace('K', '').replace(',', '.')) * 1_000)
                            else:
                                followers = int(re.sub(r'\D', '', clean_f))
                            print(f"     📌 Seguidores detectados ({selector}): {followers}")
                            break
                except: continue
            
            # Atualiza perfil básico
            await self._update_candidate_profile(candidate_id, {'edge_followed_by': {'count': followers}, 'username': username})

            # Extração de shortcodes com seletores ultra-abrangentes
            shortcodes = await self.page.evaluate(f"""() => {{
                // Pega todos os links que contenham /p/ no href, filtrando duplicatas
                const links = Array.from(document.querySelectorAll('a'))
                    .map(a => a.getAttribute('href'))
                    .filter(href => href && href.includes('/p/'))
                    .map(href => {{
                        const parts = href.split('/');
                        return parts[parts.indexOf('p') + 1];
                    }});
                return [...new Set(links)].slice(0, {MAX_POSTS_PER_PROFILE});
            }}""")

            if not shortcodes:
                print(f"⚠️ [Headless] Nenhum post encontrado visualmente para @{username}. Tentando scroll mais profundo...")
                await self.page.mouse.wheel(0, 1500)
                await asyncio.sleep(5)
                shortcodes = await self.page.evaluate(f"() => Array.from(document.querySelectorAll('a[href^=\"/p/\"]')).map(a => a.getAttribute('href').split('/')[2]).slice(0, {MAX_POSTS_PER_PROFILE})")

            print(f"     📸 {len(shortcodes)} posts detectados.")
            for shortcode in shortcodes:
                await self._scrape_post_comments(username, shortcode)

        except PlaywrightTimeoutError:
            print(f"❌ [Headless] Timeout ao carregar @{username}.")
        except Exception as e:
            print(f"❌ [Headless] Erro ao raspar @{username}: {e}")

    async def _extract_shared_data(self) -> Optional[Dict]:
        assert self.page is not None

        try:
            data_text = await self.page.evaluate(r"""
                () => {
                    const scripts = Array.from(document.querySelectorAll('script'));
                    for (const script of scripts) {
                        const text = script.textContent || '';
                        const match = text.match(/window\._sharedData\s*=\s*(\{[\s\S]*\});?/);
                        if (match) {
                            return match[1];
                        }
                    }
                    return null;
                }
                """)

            if not data_text:
                return None
            return json.loads(data_text)
        except Exception as e:
            print(f"⚠️ [Headless] Falha ao parsear sharedData: {e}")
            return None

    def _extract_profile_info(self, shared_data: Dict) -> Optional[Dict]:
        try:
            profile = shared_data.get('entry_data', {}).get('ProfilePage', [None])[0]
            if not profile:
                return None
            user = profile.get('graphql', {}).get('user', {})
            return user
        except Exception:
            return None

    def _extract_recent_post_shortcodes(self, profile: Dict) -> List[str]:
        edges = profile.get('edge_owner_to_timeline_media', {}).get('edges', [])
        return [edge['node']['shortcode'] for edge in edges[:MAX_POSTS_PER_PROFILE] if edge.get('node')]

    async def _scrape_post_comments(self, username: str, shortcode: str):
        assert self.page is not None
        post_url = f"https://www.instagram.com/p/{shortcode}/"
        print(f"   📰 [Headless] Carregando post {shortcode}...")

        try:
            await self.page.goto(post_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            
            # Scroll para carregar comentários
            await self.page.mouse.wheel(0, 1000)
            await asyncio.sleep(2)

            comments = await self._extract_comments_from_dom()

            saved = 0
            for comment in comments[:MAX_COMMENTS_PER_POST]:
                if self._save_comment(username, shortcode, comment):
                    saved += 1

            print(f"     ✅ Post {shortcode}: {saved}/{len(comments)} comentários salvos.")
        except PlaywrightTimeoutError:
            print(f"❌ [Headless] Timeout ao carregar post {shortcode}.")
        except Exception as e:
            print(f"❌ [Headless] Erro no post {shortcode}: {e}")

    async def _extract_comments_from_dom(self) -> List[Dict]:
        assert self.page is not None
        comments = []
        try:
            # Seletores ultra-genéricos para comentários no Instagram 2026
            # O Instagram costuma usar span dentro de itens de lista ou divs repetidas
            # Vamos buscar por elementos que tenham estrutura de autor + texto
            comment_items = await self.page.query_selector_all('div[role="button"], li, div.x9f619')
            for item in comment_items:
                try:
                    # Filtra apenas itens que pareçam comentários (têm link de perfil e texto longo)
                    author_el = await item.query_selector('a[href*="/"]')
                    text_el = await item.query_selector('span')
                    
                    if author_el and text_el:
                        author = await author_el.get_attribute('href')
                        author = author.strip('/').split('/')[-1] if author else None
                        text = await text_el.inner_text()
                        
                        if author and text and len(text) > 5:
                             # Lista de exclusão de domínios/termos técnicos
                             blacklist = [
                                 "about", "help", "privacy", "terms", "locations", "popular", "lite", 
                                 "threads", "meta", "careers", "instagram", "facebook", "utm_", "entrypoint"
                             ]
                             if not any(b in author.lower() or b in text.lower() for b in blacklist):
                                 # Verifica se o texto não é apenas metadata (likes, tempo)
                                if not any(x in text.lower() for x in ["curtidas", "responder", "ver tradu", " h ", " d ", " min "]):
                                    comments.append({
                                        'id': None, 
                                        'owner_username': author, 
                                        'text': text.strip(), 
                                        'created_at': None, 
                                        'likes': 0
                                    })
                except: continue
        except Exception as e:
            print(f"     ⚠️ Erro no DOM extractor: {e}")
        
        # Deduplicação básica por texto
        unique_comments = []
        seen_texts = set()
        for c in comments:
            if c['text'] not in seen_texts:
                unique_comments.append(c)
                seen_texts.add(c['text'])
                
        return unique_comments

    def _save_comment(self, username: str, shortcode: str, comment: Dict) -> bool:
        if not comment.get('owner_username') or not comment.get('text'):
            return False

        external_id = comment.get('id') or f"ig_{username}_{shortcode}_{hash(comment['text'])}"
        comment_data = {
            'candidato_id': username,
            'post_id': shortcode,
            'autor_username': comment['owner_username'],
            'texto_bruto': comment['text'],
            'plataforma': 'INSTAGRAM',
            'data_coleta': datetime.now(timezone.utc).isoformat(),
            'processado_ia': False,
            'id_externo': f"ig_{external_id}"
        }
        try:
            supabase.table('comentarios').insert(comment_data).execute()
            return True
        except Exception:
            return False

    async def _update_candidate_profile(self, candidate_id: str, profile: Dict):
        followers = profile.get('edge_followed_by', {}).get('count')
        try:
            supabase.table('candidatos').update({
                'seguidores': followers,
                'last_scraped_at': datetime.now(timezone.utc).isoformat()
            }).eq('id', candidate_id).execute()
            print(f"     📌 @{profile.get('username')} atualizado com {followers} seguidores.")
        except Exception as e:
            print(f"⚠️ [Headless] Erro ao atualizar candidato {candidate_id}: {e}")

if __name__ == '__main__':
    asyncio.run(InstagramHeadlessScraper().run())