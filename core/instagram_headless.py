
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import hashlib
import re
import json
import asyncio
import random
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from supabase import create_client
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
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
        try:
            res = (supabase.table('scraping_accounts')
                .select('*')
                .eq('status', 'ACTIVE')
                .order('last_used_at', desc=False)
                .limit(1)
                .execute())

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
        if account_id == 'env_fallback':
            return
        try:
            supabase.table('scraping_accounts').update({'status': 'BLOCKED'}).eq('id', account_id).execute()
        except Exception:
            pass

    async def mark_shadowbanned(self, account_id: str):
        if account_id == 'env_fallback':
            return
        print(f"👻 [Identity] Conta {account_id} detectada com SHADOWBAN!")
        try:
            supabase.table('scraping_accounts').update({'status': 'SHADOWBANNED'}).eq('id', account_id).execute()
        except Exception:
            pass

    async def update_usage(self, account_id: str, session_id: Optional[str] = None):
        if account_id == 'env_fallback':
            return
        data = {'last_used_at': datetime.now(timezone.utc).isoformat()}
        if session_id:
            data['session_id'] = session_id
        try:
            supabase.table('scraping_accounts').update(data).eq('id', account_id).execute()
        except Exception:
            pass


class ProxyManager:
    """Gerencia a rotação de proxies para evitar bloqueios."""

    def __init__(self):
        self.proxies: List[Optional[Dict[str, str]]] = []
        self.current_proxy: Optional[Dict[str, str]] = None
        self._load_proxies()

    def _load_proxies(self):
        proxy_list_str = os.getenv("PROXY_LIST", "")
        if proxy_list_str:
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

        self.proxies.append(None) # Sempre incluir a opção de não usar proxy

    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        if not self.proxies:
            return None

        if self.current_proxy is None:
            self.current_proxy = self.proxies[0]
        else:
            try:
                current_index = self.proxies.index(self.current_proxy)
                self.current_proxy = self.proxies[(current_index + 1) % len(self.proxies)]
            except (ValueError, IndexError):
                self.current_proxy = self.proxies[0]

        if self.current_proxy:
            print(f"🌐 [Proxy] Usando proxy: {self.current_proxy['server']}")
        else:
            print("🌐 [Proxy] Sem proxy ativo.")
        return self.current_proxy

    def mark_bad_proxy(self):
        # Se o proxy atual foi marcado como ruim, vamos para o próximo na próxima chamada
        if self.current_proxy:
            print(f"⚠️ [Proxy] Marcando proxy atual como ruim: {self.current_proxy.get('server', 'N/A')}")
            # Para simplificar, apenas setamos para None para forçar a seleção do próximo na próxima chamada
            self.current_proxy = None


class InstagramHeadlessScraper:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.im = IdentityManager()
        self.pm = ProxyManager()
        self.active_account: Optional[Dict] = None
        self.validator = None # Para ser definido externamente

    def set_validator(self, validator):
        self.validator = validator

    async def run(self, limit: int = 15, targets: List[Dict] = None,
                  test_username: str = None, max_retries: int = 3):
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

        # ✅ CORREÇÃO: garantir que cada target tenha um registro válido no banco para obter UUID
        normalized_targets = []
        for t in targets:
            username = None
            if isinstance(t, dict) and t.get('username'):
                username = t['username']
            elif isinstance(t, str) and t:
                username = t
            
            if not username:
                print(f"⚠️ [Headless] Target inválido ignorado: {t}")
                continue

            # Garante existência no banco
            try:
                res = supabase.table('candidatos').select('id').eq('username', username).execute()
                if not res.data:
                    # Cria registro básico
                    novo = {
                        'username': username,
                        'nome_completo': username,
                        'cargo': 'Candidato',
                        'status_monitoramento': 'Ativo',
                        'prioridade_coleta': 3,
                        'data_entrada': datetime.now(timezone.utc).isoformat()
                    }
                    insert_res = supabase.table('candidatos').insert(novo).execute()
                    if insert_res.data:
                        target_data = {'id': insert_res.data[0]['id'], 'username': username}
                        print(f"✅ [Headless] @{username} auto-cadastrado (UUID: {target_data['id']})")
                        normalized_targets.append(target_data)
                    else:
                        print(f"⚠️ [Headless] Não foi possível cadastrar @{username}. Pulando.")
                else:
                    normalized_targets.append({'id': res.data[0]['id'], 'username': username})
            except Exception as e:
                print(f"❌ [Headless] Erro ao validar @{username} no banco: {e}")
                continue

        targets = normalized_targets

        if not targets:
            print("✅ [Headless] Nenhum alvo válido após normalização.")
            return

        pending_targets = list(targets)

        async with async_playwright() as pw:
            self.playwright = pw

            while pending_targets:
                candidate = pending_targets.pop(0)
                username = candidate.get('username')
                if not username:
                    continue

                success = False
                for attempt in range(max_retries):
                    print(f"🎯 [Headless] Raspando @{username} (Tentativa {attempt + 1}/{max_retries})...")

                    proxy_config = self.pm.get_next_proxy()

                    try:
                        self.browser = await pw.chromium.launch(
                            headless=PLAYWRIGHT_HEADLESS,
                            proxy=proxy_config,
                            args=[
                                "--disable-blink-features=AutomationControlled",
                                "--no-sandbox",
                                "--disable-dev-shm-usage"
                            ],
                        )
                        context = await self.browser.new_context(
                            viewport={"width": 1280, "height": 800},
                            locale="pt-BR",
                            user_agent=(
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/120.0.0.0 Safari/537.36" # User-agent atualizado
                            ),
                        )

                        if self.active_account.get('session_id'):
                            await context.add_cookies([{
                                'name': 'sessionid',
                                'value': self.active_account['session_id'],
                                'domain': '.instagram.com',
                                'path': '/'
                            }])

                        self.page = await context.new_page()
                        self.page.set_default_timeout(120000) # Aumentado timeout geral

                        if not await self._ensure_logged_in():
                            print(f"❌ [Headless] Falha crítica no login ou sessão. Conta @{self.active_account['username']} pode estar bloqueada.")
                            await self.im.mark_blocked(self.active_account['id'])
                            # Se o login falhar repetidamente, precisamos parar
                            if attempt == max_retries - 1:
                                print("🚫 [Headless] Todas as tentativas de login falharam. Interrompendo.")
                                return
                            continue # Tenta novamente com outra conta/proxy

                        if await self._scrape_candidate_profile(candidate):
                            success = True
                            break
                        else:
                            # Se _scrape_candidate_profile retornou False, pode ser por perfil privado ou sem posts
                            # Consideramos sucesso para avançar para o próximo alvo
                            success = True
                            break

                    except PlaywrightTimeoutError as e:
                        print(f"🔥 [Headless] Timeout durante operação para @{username} (Tentativa {attempt + 1}): {e}")
                        self.pm.mark_bad_proxy()
                        if attempt == max_retries - 1:
                            print(f"☠️ [Headless] Falha ao raspar @{username} após {max_retries} tentativas devido a timeouts.")
                    except PlaywrightError as e:
                        print(f"🛑 [Headless] Erro do Playwright (ex: Target Closed) para @{username}: {e}")
                        if "Target closed" in str(e) or "Browser closed" in str(e):
                            print("🔄 [Headless] Navegador fechado inesperadamente. Reiniciando para o próximo alvo.")
                        if attempt == max_retries - 1:
                            print(f"☠️ [Headless] Falha ao raspar @{username} após {max_retries} tentativas devido a erros de navegador.")
                    except Exception as e:
                        print(f"❌ [Headless] Erro inesperado para @{username} (Tentativa {attempt + 1}): {type(e).__name__} - {e}")
                        # Tenta identificar se é um bloqueio
                        if "challenge_required" in str(e) or "login_required" in str(e):
                             print("🚨 [Headless] Bloqueio detectado. Tentando outra conta.")
                             await self.im.mark_shadowbanned(self.active_account['id'])
                             self.active_account = await self.im.get_next_available_account() # Tenta obter nova conta
                             if not self.active_account:
                                 print("🚫 [Headless] Sem contas alternativas disponíveis. Interrompendo.")
                                 return
                        self.pm.mark_bad_proxy()
                        if attempt == max_retries - 1:
                            print(f"☠️ [Headless] Falha ao raspar @{username} após {max_retries} tentativas devido a erros.")
                    finally:
                        if self.browser:
                            await self.browser.close()
                        await asyncio.sleep(random.uniform(5, 10)) # Pausa maior entre tentativas/alvos

                if not success:
                    print(f"☠️ [Headless] Falha crítica ao processar @{username}.")
                else:
                    # Atualiza o uso da conta mesmo se não for um sucesso completo (ex: perfil privado)
                    await self.im.update_usage(self.active_account['id'])

        print("✅ [Headless] Ciclo de raspagem finalizado.")

    async def _ensure_logged_in(self) -> bool:
        try:
            await asyncio.sleep(random.uniform(2, 4)) # Pequena pausa antes de verificar
            # Verifica se já está logado acessando uma página que exige login
            await self.page.goto("https://www.instagram.com/", wait_until="networkidle", timeout=60000) # Aumentado timeout para carregamento da página inicial
            await asyncio.sleep(random.uniform(3, 6))

            # Verifica se o formulário de login está visível (sessão expirada/inválida)
            # ou se a URL mudou para /accounts/login/
            login_form_present = await self.page.locator('input[name="username"]').count() > 0
            is_login_url = "/accounts/login/" in self.page.url

            if login_form_present or is_login_url:
                print(f"🔑 [Headless] Sessão expirada ou inválida (detectada via {'form' if login_form_present else 'URL'}). Tentando login para @{self.active_account['username']}...")
                
                # Se não estiver na URL de login mas o form estiver lá, tenta navegar explicitamente para garantir
                if not is_login_url:
                    await self.page.goto(INSTAGRAM_LOGIN_URL, timeout=60000)
                    await asyncio.sleep(random.uniform(1, 3))

                # Preenche os campos de login
                await self.page.fill('input[name="username"]', self.active_account['username'])
                await asyncio.sleep(random.uniform(0.5, 1.5))
                await self.page.fill('input[name="password"]', self.active_account['password'])
                await asyncio.sleep(random.uniform(1, 2))

                # Clica no botão de submit e aguarda o carregamento da página
                await self.page.click('button[type="submit"]')
                await self.page.wait_for_load_state("networkidle", timeout=120000) # Timeout maior para login
                await asyncio.sleep(random.uniform(3, 5))

                # Verifica se o formulário ainda está presente após a tentativa
                if await self.page.locator('input[name="username"]').count() > 0:
                    print("❌ [Headless] Login falhou. Verifique credenciais ou status da conta.")
                    return False

                print("✅ [Headless] Login realizado com sucesso.")
                # Salva o cookie de sessão se encontrado
                cookies = await self.page.context.cookies()
                session_cookie = next((c for c in cookies if c['name'] == 'sessionid'), None)
                if session_cookie:
                    await self.im.update_usage(self.active_account['id'], session_cookie['value'])
                return True
            else:
                print("✅ [Headless] Sessão de login ativa (interface logada detectada).")
                return True # Já estava logado

        except PlaywrightTimeoutError:
            print("🔥 [Headless] Timeout durante a verificação ou processo de login.")
            return False
        except Exception as e:
            print(f"❌ [Headless] Erro durante _ensure_logged_in: {type(e).__name__} - {e}")
            return False

    def _load_pending_targets(self, limit: int) -> List[Dict]:
        print(f"⏳ [Headless] Carregando até {limit} alvos pendentes do banco de dados...")
        try:
            # Busca candidatos que ainda não foram raspados ou foram raspados há muito tempo
            res = (supabase.table('candidatos') 
                .select('id,username') 
                .order('last_scraped_at', desc=False, nullsfirst=True) 
                .limit(limit) 
                .execute())
            print(f"🔍 [Headless] Encontrados {len(res.data)} alvos pendentes.")
            return res.data or []
        except Exception as e:
            print(f"❌ [DB] Erro ao carregar alvos pendentes: {e}")
            return []

    async def _fetch_profile_data(self, username: str) -> Optional[Dict[str, Any]]:
        print(f"  📄 [Headless] Buscando dados do perfil @{username}...")
        try:
            await asyncio.sleep(random.uniform(3, 6))
            await self.page.goto(f"https://www.instagram.com/{username}/", timeout=90000)
            await asyncio.sleep(random.uniform(4, 7))

            # Força o carregamento do feed rolando a página
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2)
            await self.page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)

            page_content = await self.page.content()

            profile_data = {
                'username': username,
                'full_name': '',
                'biography': '',
                'follower_count': 0,
                'following_count': 0,
                'media_count': 0,
                'is_verified': False,
                'is_private': False,
                'profile_pic_url': None,
                'external_url': None,
                'post_shortcodes': []
            }

            # 1. Tenta JSON-LD (script embutido)
            json_ld_match = re.search(
                r'<script type="application/ld\+json">(.*?)</script>',
                page_content,
                re.DOTALL
            )
            if json_ld_match:
                try:
                    ld_data = json.loads(json_ld_match.group(1))
                    main_entity = ld_data.get('mainEntity', ld_data)
                    profile_data['full_name'] = main_entity.get('name', username)
                    profile_data['biography'] = main_entity.get('description', '')
                    profile_data['is_private'] = not main_entity.get('isAccessibleForFree', True)
                    profile_data['is_verified'] = main_entity.get('isVerified', False)
                    img = main_entity.get('image', {})
                    if isinstance(img, dict):
                        profile_data['profile_pic_url'] = img.get('url')
                    profile_data['external_url'] = main_entity.get('url', '')
                except Exception as e:
                    print(f"  ⚠️ [Headless] JSON-LD parse error: {e}")

            # 2. Tenta __INITIAL_STATE__ (JavaScript embutido)
            if not profile_data['full_name']:
                js_data = await self.page.evaluate("""() => {
                    const user = window.__INITIAL_STATE__?.ProfilePage?.[0]?.graphql?.user;
                    if (!user) return null;
                    return {
                        full_name: user.full_name,
                        biography: user.biography,
                        follower_count: user.edge_followed_by?.count || 0,
                        following_count: user.edge_follow?.count || 0,
                        media_count: user.edge_owner_to_timeline_media?.count || 0,
                        is_verified: user.is_verified,
                        is_private: user.is_private,
                        profile_pic_url: user.profile_pic_url,
                        external_url: user.external_url
                    };
                }""")
                if js_data:
                    profile_data.update(js_data)

            # 3. Fallback para meta tags
            if not profile_data['full_name']:
                meta_name = await self.page.locator('meta[property="og:title"]').get_attribute('content')
                if meta_name:
                    profile_data['full_name'] = meta_name.split(' (@')[0] if ' (@' in meta_name else meta_name

            # Contagens via UI se ainda estiverem zeradas
            if (profile_data['follower_count'] == 0 or profile_data['media_count'] == 0):
                try:
                    follower_el = await self.page.locator('xpath=//*[text()="seguidores" or text()="seguindo"]').first
                    parent = await follower_el.locator("xpath='ancestor::div[@role=\"button\"]'").first
                    count_text = await parent.text_content() if parent else ''
                    match_f = re.search(r'([\d.,]+)\s+seguidores', count_text.replace('.', ''))
                    match_m = re.search(r'([\d.,]+)\s+publicações', count_text.replace('.', ''))
                    if match_f:
                        profile_data['follower_count'] = int(match_f.group(1))
                    if match_m:
                        profile_data['media_count'] = int(match_m.group(1))
                except Exception:
                    pass

            # Shortcodes dos posts via JavaScript para lidar com renderização dinâmica
            shortcodes_found = await self.page.evaluate("""() => {
                const links = document.querySelectorAll('a[href*="/p/"], a[href*="/reel/"]');
                const codes = [];
                for (const link of links) {
                    const href = link.getAttribute('href');
                    if (href) {
                        const match = href.match(/\/(p|reel)\/([A-Za-z0-9_-]{10,12})/);
                        if (match && codes.indexOf(match[2]) === -1) {
                            codes.push(match[2]);
                        }
                    }
                }
                return codes.slice(0, 5);
            }""")

            if shortcodes_found:
                seen = set()
                profile_data['post_shortcodes'] = [s for s in shortcodes_found if not (s in seen or seen.add(s))][:MAX_POSTS_PER_PROFILE]
                print(f"  📸 [Headless] @{username}: {len(profile_data['post_shortcodes'])} posts encontrados via JavaScript.")
            else:
                print(f"  ⚠️ [Headless] Nenhum post encontrado via JavaScript. Tentando fallback estático...")
                shortcodes_found = re.findall(r'href="/p/([A-Za-z0-9_-]{10,12})/', page_content)
                seen = set()
                profile_data['post_shortcodes'] = [s for s in shortcodes_found if not (s in seen or seen.add(s))][:MAX_POSTS_PER_PROFILE]
                print(f"  📸 [Headless] @{username}: {len(profile_data['post_shortcodes'])} posts via regex fallback.")

            if await self.page.locator('h2:has-text("Esta conta é privada")').count() > 0:
                profile_data['is_private'] = True

            return profile_data

        except PlaywrightTimeoutError:
            print(f"  🔥 [Headless] Timeout ao buscar perfil @{username}.")
            return None
        except Exception as e:
            print(f"  ❌ [Headless] Erro ao buscar perfil @{username}: {e}")
            return None

    async def _scrape_candidate_profile(self, candidate: Any) -> bool:
        """
        Busca os dados do perfil e, se não for privado e tiver posts recentes,
        inicia a coleta de comentários para cada post.
        """
        username = candidate.get('username')
        if not username:
            print("  ❌ [Headless] Candidate object malformado, missing 'username'.")
            return False

        print(f"  📄 [Headless] Processando perfil de @{username}...")

        profile_data = await self._fetch_profile_data(username)
        if not profile_data:
            print(f"  ❌ [Headless] Falha ao obter dados do perfil para @{username}. Pulando.")
            return False

        # Salva os dados do perfil IMEDIATAMENTE, mesmo que privado ou sem posts
        self._update_candidate_data(candidate.get('id'), profile_data)

        if profile_data.get('is_private'):
            print(f"  🔒 [Headless] Perfil @{username} é privado. Pulando coleta de posts/comentários.")
            return True # Retorna True para indicar que o processamento do *candidato* foi concluído, mesmo que sem coleta

        shortcodes = profile_data.get('post_shortcodes', [])

        if not shortcodes:
            print(f"  - [Headless] @{username} não tem posts recentes visíveis ou o link para eles não foi encontrado. Pulando coleta de comentários.")
            return True # Retorna True para indicar conclusão

        # ✅ CORREÇÃO: agora realmente itera os shortcodes obtidos e coleta comentários
        print(f"  💬 [Headless] Iniciando coleta de comentários de {len(shortcodes)} posts de @{username}...")
        for shortcode in shortcodes:
            try:
                await self._scrape_post(username, shortcode)
                # Pausa humana entre posts para simular navegação
                await asyncio.sleep(random.uniform(5, 10))
            except Exception as e:
                print(f"  ⚠️ [Headless] Erro ao processar post {shortcode} de @{username}: {type(e).__name__} - {e}")
                # Continua para o próximo post mesmo se um falhar
                continue

        print(f"  ✅ [Headless] Processamento do perfil @{username} concluído.")
        return True

    def _update_candidate_data(self, candidate_id: str, profile_data: Dict[str, Any]):
        """Atualiza os dados do candidato no banco de dados."""
        if not candidate_id:
            return

        update_data = {
            'nome_completo': profile_data.get('full_name'),
            'bio': profile_data.get('biography'),
            'seguidores': profile_data.get('follower_count'),
            'last_scraped_at': datetime.now(timezone.utc).isoformat()
        }
        # Remove chaves com valor None
        update_data = {k: v for k, v in update_data.items() if v is not None}

        try:
            (supabase.table('candidatos')
             .update(update_data)
             .eq('id', candidate_id)
             .execute())
            print(f"  📝 [Headless] Candidato @{profile_data.get('username', candidate_id)} atualizado.")
        except Exception as e:
            print(f"  ❌ [Headless] Erro ao atualizar candidato {candidate_id}: {e}")

    async def _scrape_post(self, username: str, shortcode: str):
        print(f"  📌 [Headless] Coletando post /{shortcode}/ de @{username}...")
        try:
            await self.page.goto(f"https://www.instagram.com/p/{shortcode}/", timeout=90000)
            await asyncio.sleep(random.uniform(4, 8))

            for _ in range(3):
                await self.page.mouse.wheel(0, 1000)
                await asyncio.sleep(random.uniform(2, 4))

            comments_data = []

            # 1. Extração via DOM
            try:
                dom_comments = await self.page.evaluate("""() => {
                    const items = Array.from(document.querySelectorAll('ul li'));
                    return items.map(li => {
                        const authorEl = li.querySelector('h3 a, h4 a, a[role="link"]');
                        const textEl = li.querySelector('span._ap30, span[dir="auto"]');
                        const author = authorEl ? authorEl.innerText.trim() : null;
                        const text = textEl ? textEl.innerText.trim() : null;
                        if (author && text && text.length > 2) return { author, text };
                        return null;
                    }).filter(i => i !== null);
                }""")
                comments_data.extend(dom_comments)
                print(f"  💬 [Headless] DOM: {len(dom_comments)} comentários brutos.")
            except Exception as e:
                print(f"  ⚠️ [Headless] DOM falhou: {e}")

            # 2. Regex Fallback Aprimorado
            if len(comments_data) < MAX_COMMENTS_PER_POST / 2:
                print(f"  🔍 [Headless] Regex Fallback para /{shortcode}/...")
                html_content = await self.page.content()
                pattern_comments = re.compile(
                    r'\"text\"\s*:\s*\"((?:[^\"\\]|\\.)*?)\".*?'
                    r'\"owner\"\s*:\{.*?\"username\"\s*:\s*\"([^\"]+)\"',
                    re.DOTALL
                )
                matches = pattern_comments.findall(html_content)
                temp = []
                for text, author in matches:
                    try:
                        text = json.loads(f'"{text}"')
                    except:
                        try:
                            text = text.encode().decode('unicode_escape')
                        except:
                            pass
                    text = text.strip()
                    author = author.strip()
                    if len(text) > 2 and author.lower() != username.lower():
                        temp.append({'author': author, 'text': text})

                if len(temp) < MAX_COMMENTS_PER_POST / 2:
                    alt_pattern = re.compile(
                        r'\"text\"\s*:\s*\"((?:[^\"\\]|\\.){3,500})\".*?'
                        r'\"username\"\s*:\s*\"([^\"]+)\"',
                        re.DOTALL
                    )
                    for text, author in alt_pattern.findall(html_content):
                        text = text.strip()
                        author = author.strip()
                        if len(text) > 2 and author.lower() != username.lower() and author not in ['instagram', 'meta']:
                            temp.append({'author': author, 'text': text})

                comments_data.extend(temp)
                print(f"  💬 [Headless] Regex: {len(temp)} comentários.")

            # Sanitização e salvamento
            saved = 0
            for cmd in comments_data[:MAX_COMMENTS_PER_POST]:
                if not cmd.get('author') or len(cmd['author'].strip()) < 2:
                    cmd['author'] = f"anon_{hashlib.md5(cmd['text'].encode()).hexdigest()[:8]}"
                if not cmd.get('text') or len(cmd['text'].strip()) < 3:
                    continue
                if self._save_comment(username, shortcode, cmd['text'], cmd['author']):
                    saved += 1

            print(f"  ✅ [Headless] {saved} comentários salvos de /{shortcode}/.")

        except PlaywrightTimeoutError:
            print(f"  🔥 [Headless] Timeout no post /{shortcode}/.")
        except Exception as e:
            print(f"  ❌ [Headless] Erro no post /{shortcode}/: {e}")

    def _save_comment(self, candidato_username: str, shortcode: str, text: str, author: str) -> bool:
        """Valida, limpa e persiste um comentário no Supabase. Retorna True se salvo."""
        # Garante que text e author são strings e remove espaços em branco excessivos
        text = str(text or '').strip()
        author = str(author or '').strip()

        # Validações básicas antes de tentar limpar ou salvar
        if not text or len(text) < 3:
            return False
        if not author or len(author) < 2:
            return False
        if author.lower() == candidato_username.lower(): # Ignora comentários do próprio candidato
            return False

        # Limpa o texto do comentário usando a função text_processor
        valid_text = clean_comment(text, candidato_username)
        if not valid_text:
            return False

        import hashlib
        # Garante que o id_externo NUNCA seja nulo
        base_string = f"{author}_{shortcode}_{valid_text[:50]}_{datetime.now(timezone.utc).isoformat()}"
        generated_id = f"ig_{hashlib.md5(base_string.encode()).hexdigest()[:12]}"

        # Dados a serem inseridos no banco de dados
        data = {
            'id_externo': generated_id,
            'candidato_id': candidato_username,
            'post_id': shortcode,
            'autor_username': author,
            'texto_bruto': valid_text,
            'plataforma': 'INSTAGRAM',
            'data_coleta': datetime.now(timezone.utc).isoformat(),
            'processado_ia': False, # Flag para processamento posterior pela IA
            'mined': True
        }

        # Se um validador foi definido (do Quality Gate), usa-o antes de salvar
        if self.validator:
            if not self.validator.evaluate_payload("InstagramHeadlessScraper", data):
                print(f"  ⚠️ [Headless] Comentário de @{author} para post {shortcode} descartado pelo Quality Gate.")
                return False

        # Tenta inserir os dados no banco de dados Supabase
        try:
            res = supabase.table('comentarios').insert(data).execute()
            if res.data:
                # print(f"  💾 [Headless] Comentário de @{author} salvo: '{valid_text[:50]}...'") # Log opcional para comentários salvos
                return True
            else:
                print(f"  ⚠️ [Headless] Inserção de comentário de @{author} para post {shortcode} não retornou dados, pode ser duplicado ou erro DB.")
                # Verifica se o erro é de duplicidade (código 23505)
                if res.error and 'duplicate key' in res.error.message:
                    return False # Não é um erro crítico, apenas duplicado
                elif res.error:
                    print(f"  ❌ [Headless] Erro ao inserir comentário de @{author}: {res.error.message}")
                    return False
                return False # Retorna False em caso de sucesso mas sem dados (situação inesperada)
        except Exception as e:
            print(f"  ❌ [Headless] Exceção ao persistir comentário de @{author} para post {shortcode}: {type(e).__name__} - {e}")
            return False


if __name__ == '__main__':
    # Exemplo de como executar o scraper
    # asyncio.run(InstagramHeadlessScraper().run(test_username="example_user"))
    # asyncio.run(InstagramHeadlessScraper().run(limit=10)) # Executa com limite de 10 alvos
    asyncio.run(InstagramHeadlessScraper().run()) # Executa com o limite padrão e alvos do DB

