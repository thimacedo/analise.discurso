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
PLAYWRIGHT_HEADLESS = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
MAX_POSTS_PER_PROFILE = int(os.getenv("MAX_POSTS_PER_PROFILE", "3"))
MAX_COMMENTS_PER_POST = int(os.getenv("MAX_COMMENTS_PER_POST", "50"))

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
            )

            if INSTAGRAM_SESSIONID:
                await context.add_cookies([
                    {
                        "name": "sessionid",
                        "value": INSTAGRAM_SESSIONID,
                        "domain": ".instagram.com",
                        "path": "/",
                    }
                ])

            self.page = await context.new_page()
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
            await self.page.goto("https://www.instagram.com/", wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            if await self.page.locator('input[name="username"]').count() > 0:
                if not IG_USER or not IG_PASS:
                    print("❌ [Headless] Não há credenciais IG_USER/IG_PASS para login.")
                    return False

                print("🔑 [Headless] Login via Playwright...")
                await self.page.fill('input[name="username"]', IG_USER)
                await self.page.fill('input[name="password"]', IG_PASS)
                await asyncio.sleep(1)
                await self.page.click('button[type="submit"]')
                await self.page.wait_for_load_state("networkidle", timeout=30000)
                await asyncio.sleep(3)

                if await self.page.locator('input[name="username"]').count() > 0:
                    print("❌ [Headless] Login não foi possível. Verifique credenciais ou 2FA.")
                    return False
            else:
                print("✅ [Headless] Sessão válida encontrada via cookie ou login automático.")

            return True
        except PlaywrightTimeoutError:
            print("❌ [Headless] Timeout durante autenticação no Instagram.")
            return False
        except Exception as e:
            print(f"❌ [Headless] Erro durante autenticação: {e}")
            return False

    async def _scrape_candidate(self, candidate: Dict):
        username = candidate.get('username')
        candidate_id = candidate.get('id')
        if not username:
            return

        print(f"\n🎯 [Headless] Raspando @{username}...")
        profile_url = f"https://www.instagram.com/{username}/"

        try:
            await self.page.goto(profile_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            shared_data = await self._extract_shared_data()
            if not shared_data:
                print(f"⚠️ [Headless] Não foi possível extrair dados para @{username}.")
                return

            profile = self._extract_profile_info(shared_data)
            if not profile:
                print(f"⚠️ [Headless] Perfil @{username} não retornou dados válidos.")
                return

            await self._update_candidate_profile(candidate_id, profile)

            shortcodes = self._extract_recent_post_shortcodes(profile)
            if not shortcodes:
                print(f"⚠️ [Headless] Nenhum post encontrado para @{username}.")
                return

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
            await self.page.goto(post_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            shared_data = await self._extract_shared_data()
            comments = self._extract_comments(shared_data)
            if not comments:
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

    def _extract_comments(self, shared_data: Optional[Dict]) -> List[Dict]:
        if not shared_data:
            return []
        try:
            post_data = shared_data.get('entry_data', {}).get('PostPage', [None])[0]
            if not post_data:
                return []
            media = post_data.get('graphql', {}).get('shortcode_media', {})
            edges = media.get('edge_media_to_parent_comment', {}).get('edges', [])
            comments = []
            for edge in edges:
                node = edge.get('node', {})
                comments.append({
                    'id': node.get('id'),
                    'owner_username': node.get('owner', {}).get('username'),
                    'text': node.get('text'),
                    'created_at': node.get('created_at'),
                    'likes': node.get('edge_liked_by', {}).get('count', 0)
                })
            return comments
        except Exception:
            return []

    async def _extract_comments_from_dom(self) -> List[Dict]:
        assert self.page is not None
        comments = []
        try:
            comment_items = await self.page.query_selector_all('ul > li > div > div > div.C4VMK')
            for item in comment_items[:MAX_COMMENTS_PER_POST]:
                author = await item.query_selector_eval('h3 span a', 'el => el.textContent')
                text = await item.query_selector_eval('span', 'el => el.textContent')
                if author and text:
                    comments.append({'id': None, 'owner_username': author, 'text': text, 'created_at': None, 'likes': 0})
        except Exception:
            pass
        return comments

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