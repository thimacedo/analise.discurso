import os
from datetime import datetime, timedelta, UTC
from supabase import create_client
from dotenv import load_dotenv
import httpx
import asyncio
from core.normalizer import target_normalizer
from core.election_monitor import ElectionMonitor

load_dotenv()

class TargetManager:
    def __init__(self, hours_threshold=24, stale_days=3):
        self.supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        self.threshold = hours_threshold
        self.stale_days = stale_days
        self.recently_scraped = set()
        self._load_recent_profiles()

    def _fetch(self, path, params=None):
        url = f"{os.getenv('SUPABASE_URL')}/rest/v1/{path}"
        headers = {"apikey": os.getenv("SUPABASE_KEY"), "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"}
        try:
            resp = httpx.get(url, headers=headers, params=params, timeout=15.0)
            return resp.json() if resp.status_code == 200 else []
        except Exception: return []

    def _load_recent_profiles(self):
        cutoff = (datetime.now(UTC) - timedelta(hours=self.threshold)).isoformat()
        try:
            resp = self.supabase.table('candidatos').select('username').gte('last_scraped_at', cutoff).execute()
            self.recently_scraped = {str(i['username']).lower().strip() for i in resp.data}
            if self.recently_scraped:
                print(f"📊 [TargetManager] {len(self.recently_scraped)} perfis ignorados (raspados há menos de {self.threshold}h).")
        except Exception: pass

    def filter_targets(self, target_list):
        if not target_list: return []
        
        raw = [t.get('username') if isinstance(t, dict) else str(t) for t in target_list]
        normalized = target_normalizer.normalize_list(raw)
        to_scrape = [u for u in normalized if u.lower().strip() not in self.recently_scraped]
        
        print(f"🎯 [TargetManager] {len(normalized)} alvos processados. {len(to_scrape)} pendentes.")
        return to_scrape

    def get_stale_targets(self, limit=20):
        cutoff = (datetime.now(UTC) - timedelta(days=self.stale_days)).isoformat()
        params = {
            "select": "username", 
            "or": f"(last_scraped_at.is.null,last_scraped_at.lt.{cutoff})", 
            "order": "last_scraped_at.asc", 
            "limit": str(limit)
        }
        items = self._fetch('candidatos', params=params)
        return [i['username'] for i in items if i.get('username')]

    def get_high_activity_targets(self, limit=20):
        params = {
            "select": "username", 
            "status_monitoramento": "eq.ATIVO", 
            "order": "comentarios_totais_count.desc", 
            "limit": str(limit)
        }
        items = self._fetch('candidatos', params=params)
        return [i['username'] for i in items if i.get('username')]

    async def ensure_competitor_coverage(self):
        """Garante que novos candidatos detectados por notícias sejam adicionados."""
        print("🌍 [TargetManager] Iniciando monitoramento eleitoral externo...")
        monitor = ElectionMonitor()
        activated = await monitor.update_competitor_coverage()
        if activated:
            print(f"✅ [TargetManager] {len(activated)} novos alvos ativados via monitoramento.")
        return activated

    def build_dynamic_queue(self, static_targets=None, limit=30):
        queue = target_normalizer.normalize_list(static_targets or [])
        stale = self.get_stale_targets(limit)
        active = self.get_high_activity_targets(limit)
        
        combined = queue + [t for t in stale + active if t not in queue]
        return combined[:limit*2]
