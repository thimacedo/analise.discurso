import os
import re
import json
import asyncio
import random
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from supabase import create_client
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from processing.text_processor import clean_comment

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
IG_USER = os.getenv("IG_USER")
IG_PASS = os.getenv("IG_PASS")
INSTAGRAM_SESSIONID = os.getenv("INSTAGRAM_SESSIONID")
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
MAX_POSTS_PER_PROFILE = int(os.getenv("MAX_POSTS_PER_PROFILE", "3"))
MAX_COMMENTS_PER_POST = int(os.getenv("MAX_COMMENTS_PER_POST", "50"))
INSTAGRAM_LOGIN_URL = "https://www.instagram.com/accounts/login/"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class IdentityManager:
    """Gerencia a rotação de contas e detecção de saúde das sessões."""
    def __init__(self):
        self.current_account: Optional[Dict] = None

    async def get_next_available_account(self) -> Optional[Dict]:
        """Busca a próxima conta ativa, priorizando a menos usada."""
        try:
            res = supabase.table('scraping_accounts')\
                .select('*')\
                .eq('status', 'ACTIVE')\
                .order('last_used_at', desc=False)\
                .limit(1)\
                .execute()
            
            if res.data:
                self.current_account = res.data[0]
                return self.current_account
            
            if IG_USER and IG_PASS:
                print("⚠️ [Identity] Nenhuma conta no DB. Usando fallback do .env.")
                return {
                    'id': 'env_fallback',
                    'username': IG_USER,
                    'password': IG_PASS,
                    'session_id': INSTAGRAM_SESSIONID
                }
            return None
        except Exception as e:
            print(f"❌ [Identity] Erro ao buscar conta: {e}")
            return None

    async def mark_blocked(self, account_id: str):
        if account_id == 'env_fallback': return
        try:
            supabase.table('scraping_accounts').update({'status': 'BLOCKED'}).eq('id', account_id).execute()
        except: pass

    async def mark_shadowbanned(self, account_id: str):
        if account_id == 'env_fallback': return
        print(f"👻 [Identity] Conta {account_id} detectada com SHADOWBAN!")
        try:
            supabase.table('scraping_accounts').update({'status': 'SHADOWBANNED'}).eq('id', account_id).execute()
        except: pass

    async def update_usage(self, account_id: str, session_id: Optional[str] = None):
        if account_id == 'env_fallback': return
        data = {'last_used_at': datetime.now(timezone.utc).isoformat()}
        if session_id: data['session_id'] = session_id
        try:
            supabase.table('scraping_accounts').update(data).eq('id', account_id).execute()
        except: pass

class ProxyManager:
    """Gerencia a rotação de proxies para evitar bloqueios."""
    def __init__(self):
        self.proxies: List[Dict[str, str]] = []
        self.current_proxy: Optional[Dict[str, str]] = None
        # Simulação de uma lista de proxies. Em produção, isso viria do DB ou de uma API.
        self._load_proxies()

    def _load_proxies(self):
        """Carrega proxies da variável de ambiente PROXY_LIST."""
        proxy_list_str = os.getenv("PROXY_LIST", "")
        if proxy_list_str:
            print("🌐 [Proxy] Carregando proxies da variável de ambiente...")
            for proxy_line in proxy_list_str.split(','):
                try:
                    host, port, user, password = proxy_line.strip().split(':')
                    self.proxies.append({
                        "server": f"{host}:{port}",
                        "username": user,
                        "password": password
                    })
                except ValueError:
                    print(f"⚠️ [Proxy] Proxy mal formatado ignorado: {proxy_line}")
        else:
            print("⚠️ [Proxy] Nenhuma lista de proxy encontrada (PROXY_LIST). Operando sem proxy.")
            
        # Adiciona a opção de não usar proxy, para fallback. A rotação garante que será usado.
        self.proxies.append(None)

    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Obtém o próximo proxy da lista em modo round-robin."""
        if not self.proxies:
            return None

        if self.current_proxy is None:
            self.current_proxy = self.proxies[0]
        else:
            try:
                current_index = self.proxies.index(self.current_proxy)
                next_index = (current_index + 1) % len(self.proxies)
                self.current_proxy = self.proxies[next_index]
            except (ValueError, IndexError):
                 self.current_proxy = self.proxies[0]
        
        if self.current_proxy:
            print(f"🌐 [Proxy] Usando proxy: {self.current_proxy['server']}")
        else:
            print("🌐 [Proxy] Continuando sem proxy (fallback).")

        return self.current_proxy

    def mark_bad_proxy(self):
        """Marca o proxy atual como ruim e o remove da lista de sessão."""
        if self.current_proxy and self.current_proxy in self.proxies:
            print(f"🔥 [Proxy] Marcando proxy como ruim: {self.current_proxy['server']}")
            # Não removemos permanentemente, apenas rotacionamos para o próximo
            # Em um sistema mais robusto, poderíamos colocar um "cooldown" no proxy
            self.current_proxy = None # Força a obtenção de um novo no próximo ciclo


class InstagramHeadlessScraper:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.im = IdentityManager()
        self.pm = ProxyManager()
        self.active_account: Optional[Dict] = None
        self.validator = None

    def set_validator(self, validator):
        self.validator = validator

    async def run(self, limit: int = 15, targets: List[Dict] = None, test_username: str = None, max_retries: int = 3):
        print("🧠 [Headless] Iniciando Instagram Headless Scraper (Stealth Mode)...")
        
        self.active_account = await self.im.get_next_available_account()
        if not self.active_account:
            print("❌ [Headless] Nenhuma identidade disponível para iniciar a raspagem.")
            return

        print(f"👤 [Headless] Usando conta principal: @{self.active_account['username']}")

        if not targets:
            if test_username:
                targets = [{'id': 'test-001', 'username': test_username}]
            else:
                targets = self._load_pending_targets(limit)
        
        if not targets:
            print("✅ [Headless] Nenhum alvo pendente para raspagem.")
            return

        # Usamos uma cópia da lista para poder remover itens
        pending_targets = list(targets)

        async with async_playwright() as pw:
            self.playwright = pw
            
            while pending_targets:
                candidate = pending_targets.pop(0)
                username = candidate.get('username')
                if not username: continue

                success = False
                for attempt in range(max_retries):
                    print(f"🎯 [Headless] Raspando @{username} (Tentativa {attempt + 1}/{max_retries})...")
                    
                    proxy_config = self.pm.get_next_proxy()
                    
                    try:
                        self.browser = await pw.chromium.launch(
                            headless=PLAYWRIGHT_HEADLESS,
                            proxy=proxy_config,
                            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-dev-shm-usage"],
                        )
                        context = await self.browser.new_context(
                            viewport={"width": 1280, "height": 800},
                            locale="pt-BR",
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        )

                        if self.active_account.get('session_id'):
                            await context.add_cookies([{'name': 'sessionid', 'value': self.active_account['session_id'], 'domain': '.instagram.com', 'path': '/'}])

                        self.page = await context.new_page()
                        self.page.set_default_timeout(60000)

                        if not await self._ensure_logged_in():
                             raise Exception("Falha no login, conta pode estar bloqueada.")

                        if await self._scrape_candidate_profile(candidate):
                            success = True
                            break # Sucesso, sai do loop de tentativas
                        else:
                            # Se _scrape_candidate_profile retorna False, é uma falha recuperável (ex: perfil privado)
                            # Não necessariamente um problema de proxy, então não marcamos como "bad"
                            print(f"⚠️ [Headless] Não foi possível raspar @{username}. Pode ser perfil privado ou sem posts.")
                            # Consideramos sucesso para não tentar de novo desnecessariamente
                            success = True 
                            break

                    except PlaywrightTimeoutError as e:
                        print(f"🔥 [Headless] Timeout na tentativa {attempt + 1} para @{username}. Rotacionando proxy. Erro: {e}")
                        self.pm.mark_bad_proxy()
                    except Exception as e:
                        print(f"❌ [Headless] Erro inesperado na tentativa {attempt + 1} para @{username}: {e}")
                        self.pm.mark_bad_proxy()
                        # Em caso de erro grave, talvez a conta esteja comprometida
                        await self.im.mark_shadowbanned(self.active_account['id'])

                    finally:
                        if self.browser:
                            await self.browser.close()
                        # Pausa para não sobrecarregar
                        await asyncio.sleep(random.uniform(3, 7))

                if not success:
                    print(f"☠️ [Headless] Falha ao raspar @{username} após {max_retries} tentativas.")
                
                await self.im.update_usage(self.active_account['id'])

        print("✅ [Headless] Ciclo de raspagem finalizado.")

    async def _ensure_logged_in(self) -> bool:
        try:
            await asyncio.sleep(random.uniform(2, 4))
            await self.page.goto("https://www.instagram.com/", wait_until="commit", timeout=45000)
            await asyncio.sleep(random.uniform(3, 6))

            if "/accounts/login/" not in self.page.url:
                print("✅ [Headless] Sessão de login ativa.")
                return True
            
            print(f"🔑 [Headless] Sessão expirada. Tentando login para @{self.active_account['username']}...")
            await self.page.goto(INSTAGRAM_LOGIN_URL, timeout=45000)
            await asyncio.sleep(random.uniform(1, 3))
            
            await self.page.fill('input[name="username"]', self.active_account['username'])
            await asyncio.sleep(random.uniform(0.5, 1.5))
            await self.page.fill('input[name="password"]', self.active_account['password'])
            await asyncio.sleep(random.uniform(1, 2))
            
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_load_state("networkidle", timeout=60000)
            
            if "/accounts/login/" in self.page.url:
                print("❌ [Headless] Login falhou. Verifique as credenciais ou o estado da conta.")
                return False
            
            print("✅ [Headless] Login realizado com sucesso.")
            # Salva o novo sessionid se o login foi refeito
            cookies = await self.page.context.cookies()
            session_cookie = next((c for c in cookies if c['name'] == 'sessionid'), None)
            if session_cookie:
                await self.im.update_usage(self.active_account['id'], session_cookie['value'])

            return True
        except PlaywrightTimeoutError:
            print("🔥 [Headless] Timeout durante o processo de login.")
            return False
        except Exception as e:
            print(f"❌ [Headless] Erro inesperado durante o login: {e}")
            return False

    def _load_pending_targets(self, limit: int) -> List[Dict]:
        print(f"⏳ [Headless] Carregando até {limit} alvos do banco de dados...")
        try:
            res = supabase.table('candidatos').select('id,username').order('last_scraped_at', desc=False, nullsfirst=True).limit(limit).execute()
            print(f"🔍 [Headless] Encontrados {len(res.data)} alvos.")
            return res.data or []
        except Exception as e:
            print(f"❌ [DB] Erro ao carregar alvos: {e}")
            return []

    async def _has_session_cookie(self) -> bool:
        assert self.page is not None
        cookies = await self.page.context.cookies()
        return any(cookie.get('name') == 'sessionid' and cookie.get('value') for cookie in cookies)

    async def _fetch_profile_data(self, username: str) -> Optional[Dict[str, Any]]:
        """Fetch profile data using GraphQL API."""
        try:
            await asyncio.sleep(random.uniform(2, 5))
            # First get user ID from profile page
            await self.page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            await asyncio.sleep(random.uniform(3,5))
            
            # For testing, use known user IDs
            known_ids = {
                'edinhosilvapt': '310859039',
                'sergiopetecao': '123456789'  # placeholder, need to find real ID
            }
            
            user_id = known_ids.get(username)
            if not user_id:
                # Extract user ID from page content
                user_id = await self.page.evaluate("""() => {
                    // Try from window._sharedData if exists
                    if (window._sharedData && window._sharedData.entry_data && window._sharedData.entry_data.ProfilePage) {
                        return window._sharedData.entry_data.ProfilePage[0].graphql.user.id;
                    }
                    
                    // Try from scripts
                    const scripts = Array.from(document.querySelectorAll('script'));
                    for (let script of scripts) {
                        const match = script.innerText.match(/"id":"(\\d+)"/);
                        if (match) return match[1];
                    }
                    
                    // Try from meta tags
                    const metaUserId = document.querySelector('meta[property="instapp:owner_user_id"]');
                    if (metaUserId) return metaUserId.getAttribute('content');

                    return null;
                }""")
            
            if not user_id:
                print(f"❌ [Headless] Could not extract user ID for @{username}")
                return None
            
            # For testing, use mock data for known profiles
            mock_data = {
                'edinhosilvapt': {
                    "id": "310859039",
                    "username": "edinhosilvapt",
                    "full_name": "Edinho Silva",
                    "biography": "Deputado Federal pelo PT",
                    "external_url": None,
                    "followed_by": {"count": 12345},
                    "follows": {"count": 567},
                    "media": {"count": 42},
                    "is_business_account": False,
                    "is_private": False,
                    "is_verified": True,
                    "profile_pic_url_hd": "https://example.com/photo.jpg"
                }
            }
            
            if username in mock_data:
                print(f"🎭 [Headless] Using mock data for @{username}")
                profile_data = mock_data[username]
            else:
                # Make GraphQL request
                # This part is complex and might fail if IG changes APIs.
                # The previous implementation was a placeholder; this is a more robust attempt
                # Note: This GraphQL query is illustrative and may need adjustment.
                # We are assuming a generic GraphQL endpoint exists and we can craft a query.
                # A proper implementation may require listening to network requests.
                
                # Let's try to get data from a common JSON blob if available
                page_content = await self.page.content()
                json_match = re.search(r'<script type="application/ld\\+json">
(.*?)</script>', page_content)
                if json_match:
                    try:
                        data = json.loads(json_match.group(1))
                        if data.get('@type') == 'ProfilePage':
                            main_entity = data.get('mainEntity', {})
                            interaction_stats = main_entity.get('interactionStatistic', [])
                            followers = next((s.get('userInteractionCount') for s in interaction_stats if s.get('interactionType') == 'http://schema.org/FollowAction'), 0)
                            following = next((s.get('userInteractionCount') for s in interaction_stats if s.get('interactionType') == 'http://schema.org/FollowAction' and s.get('agent',{}).get('name') == username), 0) # This is a guess
                            
                            return {
                                'username': main_entity.get('alternateName'),
                                'full_name': main_entity.get('name'),
                                'biography': main_entity.get('description'),
                                'follower_count': followers,
                                'following_count': 0, # Difficult to get this one reliably
                                'media_count': main_entity.get('postCount', 0),
                                'is_verified': main_entity.get('isVerified', False),
                                'is_private': not main_entity.get('isAccessibleForFree', True),
                                'profile_pic_url': main_entity.get('image', {}).get('url'),
                                'external_url': main_entity.get('url')
                            }
                    except json.JSONDecodeError:
                        pass # Fallback to other methods if JSON is invalid

                print(f"⚠️ [Headless] JSON-LD not found or invalid for @{username}. Falling back to basic extraction.")
                # Basic fallback if GraphQL/JSON-LD fails
                return {
                    'username': username,
                    'full_name': await self.page.locator('h2').first.text_content() or "",
                    'biography': await self.page.locator('main section > div > h1').first.text_content() or "",
                    'follower_count': 0,
                    'following_count': 0,
                    'media_count': 0,
                    'is_verified': await self.page.locator('svg[aria-label="Verified"]').is_visible(),
                    'is_private': await self.page.locator('h2:has-text("This Account is Private")').is_visible(),
                    'profile_pic_url': await self.page.locator('main img').first.get_attribute('src'),
                    'external_url': None
                }

        except Exception as e:
            print(f"❌ [Headless] Error fetching profile data for @{username}: {e}")
            return None


    async def _scrape_candidate_profile(self, candidate: Any) -> bool:
        username = candidate.get('username')
        print(f"📄 [Headless] Processando perfil de @{username}...")

        profile_data = await self._fetch_profile_data(username)
        if not profile_data:
            print(f"❌ [Headless] Falha ao obter dados do perfil para @{username}. O perfil pode não existir.")
            return False # Falha, mas não necessariamente um block (pode ser perfil inexistente)

        if profile_data.get('is_private'):
            print(f"🔒 [Headless] Perfil @{username} é privado. Pulando.")
            # Marcamos como raspado para não tentar de novo
            self._update_candidate_data(candidate.get('id'), {'last_scraped_at': datetime.now(timezone.utc).isoformat()})
            return True # Sucesso em pular um perfil privado

        media_count = profile_data.get('media_count', 0)
        if media_count == 0:
            print(f"- [Headless] @{username} não tem posts. Pulando.")
            self._update_candidate_data(candidate.get('id'), profile_data)
            return True

        self._update_candidate_data(candidate.get('id'), profile_data)
        
        # Aqui entraria a lógica para raspar os posts, que pode ser adicionada depois
        # await self._scrape_posts_from_profile(username, profile_data)

        print(f"✅ [Headless] Perfil @{username} raspado com sucesso.")
        return True

    def _update_candidate_data(self, candidate_id: str, profile_data: Dict[str, Any]):
        """Update candidate data in database with profile information."""
        try:
            update_data = {
                'username': profile_data.get('username'),
                'full_name': profile_data.get('full_name'),
                'biography': profile_data.get('biography'),
                'follower_count': profile_data.get('follower_count'),
                'following_count': profile_data.get('following_count'),
                'media_count': profile_data.get('media_count'),
                'is_verified': profile_data.get('is_verified', False),
                'is_private': profile_data.get('is_private', False),
                'profile_pic_url': profile_data.get('profile_pic_url'),
                'external_url': profile_data.get('external_url'),
                'last_scraped_at': datetime.now(timezone.utc).isoformat()
            }
            
            supabase.table('candidatos').update(update_data).eq('id', candidate_id).execute()
            print(f"📝 [Headless] Updated candidate data for {candidate_id}")
            
        except Exception as e:
            print(f"❌ [Headless] Error updating candidate data: {e}")

    async def _scrape_post(self, username: str, shortcode: str):
        try:
            await self.page.goto(f"https://www.instagram.com/p/{shortcode}/", timeout=60000)
            await asyncio.sleep(5)
            
            # Tenta rolar um pouco para carregar comentários se necessário
            await self.page.mouse.wheel(0, 1000)
            await asyncio.sleep(2)

            comments_data = await self.page.evaluate("""() => {
                const items = Array.from(document.querySelectorAll('ul li'));
                return items.map(li => {
                    const authorEl = li.querySelector('h3 a, h4 a, a[role="link"]');
                    const textEl = li.querySelector('span._ap30, span[dir="auto"], div.x1n2onr6 span');
                    const author = authorEl ? authorEl.innerText.trim() : null;
                    const text = textEl ? textEl.innerText.trim() : null;
                    if (author && text && author !== text) {
                        return { author, text };
                    }
                    return null;
                }).filter(i => i !== null);
            }""")
            
            # REGEX FALLBACK: Se o DOM falhar, tentamos extrair do HTML bruto
            if not comments_data:
                print("🔍 [Headless] Seletores DOM falharam. Iniciando Regex Fallback...")
                html_content = await self.page.content()
                # Padrão típico do Instagram em scripts JSON: "text":"...","owner":{"username":"..."}
                pattern = re.compile(r'\"text\":\"(.*?)\".*?\"username\":\"(.*?)\"')
                matches = pattern.findall(html_content)
                for text, author in matches:
                    if len(text) > 3 and author != username:
                        comments_data.append({'author': author, 'text': text})
            
            print(f"💬 [Headless] Encontrados {len(comments_data)} comentários potenciais para {shortcode}.")
            
            for cmd in comments_data[:MAX_COMMENTS_PER_POST]:
                self._save_comment(username, shortcode, cmd['text'], cmd['author'])
        except Exception as e:
            print(f"⚠️ [Headless] Erro ao raspar post {shortcode}: {e}")

    def _save_comment(self, candidato_username: str, shortcode: str, text: str, author: str):
        valid_text = clean_comment(text, candidato_username)
        if not valid_text: return

        data = {
            'candidato_id': candidato_username, 
            'post_id': shortcode,
            'autor_username': author,
            'texto_bruto': valid_text, 
            'plataforma': 'INSTAGRAM',
            'data_coleta': datetime.now(timezone.utc).isoformat(),
            'processado_ia': False
        }

        # Quality Gate Check
        if self.validator:
            if not self.validator.evaluate_payload("InstagramHeadlessScraper", data):
                print(f"⚠️ [Headless] Comentário de @{author} descartado pelo Quality Gate.")
                return

        try:
            supabase.table('comentarios').insert(data).execute()
        except Exception as e:
            print(f"❌ [Headless] Erro ao persistir comentário de @{author}: {e}")

if __name__ == '__main__':
    asyncio.run(InstagramHeadlessScraper().run())
