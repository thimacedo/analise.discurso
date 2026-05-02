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

class InstagramHeadlessScraper:
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.im = IdentityManager()
        self.active_account: Optional[Dict] = None

    async def run(self, limit: int = 15, targets: List[Dict] = None):
        print("🧠 [Headless] Iniciando Instagram Headless Scraper (Rotation Mode)...")
        
        self.active_account = await self.im.get_next_available_account()
        if not self.active_account:
            print("❌ [Headless] Nenhuma identidade disponível.")
            return

        print(f"👤 [Headless] Usando conta: @{self.active_account['username']}")

        async with async_playwright() as pw:
            self.playwright = pw
            self.browser = await pw.chromium.launch(
                headless=PLAYWRIGHT_HEADLESS,
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
            
            if await self._ensure_logged_in():
                if not targets:
                    targets = self._load_pending_targets(limit)
                
                for candidate in targets:
                    success = await self._scrape_candidate(candidate)
                    if not success:
                        print(f"⚠️ [Headless] Possível Shadowban ou Bloqueio na conta @{self.active_account['username']}")
                        await self.im.mark_shadowbanned(self.active_account['id'])
                        break

            await self.im.update_usage(self.active_account['id'])
            await self.browser.close()

    async def _ensure_logged_in(self) -> bool:
        try:
            await self.page.goto("https://www.instagram.com/", wait_until="commit")
            await asyncio.sleep(5)
            if "/accounts/login/" not in self.page.url: return True
            
            print(f"🔑 [Headless] Tentando login para @{self.active_account['username']}...")
            await self.page.goto(INSTAGRAM_LOGIN_URL)
            await self.page.fill('input[name="username"]', self.active_account['username'])
            await self.page.fill('input[name="password"]', self.active_account['password'])
            await self.page.click('button[type="submit"]')
            await self.page.wait_for_load_state("networkidle")
            return "/accounts/login/" not in self.page.url
        except: return False

    def _load_pending_targets(self, limit: int) -> List[Dict]:
        res = supabase.table('candidatos').select('id,username').order('last_scraped_at', desc=False).limit(limit).execute()
        return res.data or []

    async def _scrape_candidate(self, candidate: Dict) -> bool:
        username = candidate.get('username')
        print(f"🎯 [Headless] @{username}...")
        try:
            await self.page.goto(f"https://www.instagram.com/{username}/", timeout=60000)
            await asyncio.sleep(5)
            
            # Detecção de Shadowban: Se a página carrega mas não tem posts/seguidores
            shortcodes = await self.page.evaluate("() => Array.from(document.querySelectorAll('a[href^=\"/p/\"]')).map(a => a.getAttribute('href').split('/')[2])")
            if not shortcodes: return False

            for sc in shortcodes[:MAX_POSTS_PER_PROFILE]:
                await self._scrape_post(username, sc)
            return True
        except: return False

    async def _scrape_post(self, username: str, shortcode: str):
        try:
            await self.page.goto(f"https://www.instagram.com/p/{shortcode}/")
            await asyncio.sleep(3)
            comments = await self.page.evaluate("() => Array.from(document.querySelectorAll('div[role=\"button\"] span')).map(s => s.innerText).filter(t => t.length > 5)")
            for cmd in comments[:MAX_COMMENTS_PER_POST]:
                self._save_comment(username, shortcode, cmd)
        except: pass

    def _save_comment(self, username: str, shortcode: str, text: str):
        data = {
            'candidato_id': username, 'post_id': shortcode,
            'texto_bruto': text, 'plataforma': 'INSTAGRAM',
            'data_coleta': datetime.now(timezone.utc).isoformat(),
            'processado_ia': False
        }
        try: supabase.table('comentarios').insert(data).execute()
        except: pass

if __name__ == '__main__':
    asyncio.run(InstagramHeadlessScraper().run())
