import os
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv
import httpx
import asyncio
from core.election_monitor import ElectionMonitor

load_dotenv()

class TargetManager:
    def __init__(self, hours_threshold=24, stale_days=3):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }
        self.threshold = hours_threshold
        self.stale_days = stale_days
        self.recently_scraped = set()
        self._load_recent_profiles()

    def _fetch_supabase(self, path, params=None):
        url = f"{self.supabase_url}/rest/v1/{path}"
        try:
            resp = httpx.get(url, headers=self.headers, params=params, timeout=15.0)
            if resp.status_code == 200:
                return resp.json()
            print(f"⚠️ [TargetManager] Erro Supabase {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"⚠️ [TargetManager] Falha conexão Supabase: {e}")
        return []

    def _update_candidate(self, candidate_id, payload):
        try:
            self.supabase.table('candidatos').update(payload).eq('id', candidate_id).execute()
            return True
        except Exception as e:
            print(f"⚠️ [TargetManager] Erro ao atualizar candidato {candidate_id}: {e}")
            return False

    def _load_recent_profiles(self):
        """Busca no banco UMA VEZ os perfis atualizados recentemente e guarda em memória."""
        cutoff_time = (datetime.utcnow() - timedelta(hours=self.threshold)).isoformat()
        
        try:
            response = self.supabase.table('candidatos') \
                .select('username') \
                .gte('last_scraped_at', cutoff_time) \
                .execute()
            self.recently_scraped = {item['username'] for item in response.data}
            print(f"📊 [TargetManager] {len(self.recently_scraped)} perfis já atualizados nas últimas {self.threshold}h. Serão ignorados.")
        except Exception as e:
            if "column" in str(e) and "does not exist" in str(e):
                print(f"⚠️ [TargetManager] Coluna 'last_scraped_at' não encontrada. Filtro desativado até a migração SQL.")
            else:
                print(f"⚠️ [TargetManager] Erro ao buscar perfis recentes: {e}")
            self.recently_scraped = set()

    def filter_targets(self, target_list):
        """
        Recebe a lista de alvos (usernames ou objetos com 'username') e retorna apenas os que precisam ser raspados.
        """
        if not target_list:
            return []

        normalized_list = []
        for t in target_list:
            if isinstance(t, dict):
                normalized_list.append(t.get('username'))
            else:
                normalized_list.append(str(t))

        unique_targets = list({u for u in normalized_list if u})
        targets_to_scrape = [u for u in unique_targets if u not in self.recently_scraped]
        ignored_count = len(unique_targets) - len(targets_to_scrape)
        print(f"🎯 [TargetManager] {len(unique_targets)} alvos solicitados. {len(targets_to_scrape)} para raspagem. ({ignored_count} ignorados)")
        return targets_to_scrape

    def get_stale_targets(self, limit=20):
        cutoff = (datetime.utcnow() - timedelta(days=self.stale_days)).isoformat()
        params = {
            "select": "id,username,last_scraped_at,score_risco,comentarios_totais_count,seguidores",
            "or": f"(last_scraped_at.is.null,last_scraped_at=lt.{cutoff})",
            "order": "last_scraped_at.asc",
            "limit": str(limit)
        }
        items = self._fetch_supabase('candidatos', params=params)
        targets = [item['username'] for item in items if item.get('username')]
        print(f"⏱️ [TargetManager] {len(targets)} alvos estagnados/prioritários encontrados.")
        return targets

    def get_high_activity_targets(self, limit=20):
        query_fields = "id,username,cargo,status_monitoramento,score_risco,comentarios_totais_count,comentarios_odio_count,seguidores,last_scraped_at"
        order_options = ["score_risco.desc", "comentarios_totais_count.desc", "seguidores.desc"]

        for order in order_options:
            params = {
                "select": query_fields,
                "status_monitoramento": "eq.ATIVO",
                "order": order,
                "limit": str(limit)
            }
            items = self._fetch_supabase('candidatos', params=params)
            if items:
                targets = [item['username'] for item in items if item.get('username')]
                print(f"🔥 [TargetManager] Prioridade alta encontrada por {order}: {len(targets)} perfis.")
                return targets

        print("⚠️ [TargetManager] Não foi possível ordenar por atividade; usando perfis ativos padrão.")
        params = {"select": query_fields, "status_monitoramento": "eq.ATIVO", "limit": str(limit)}
        items = self._fetch_supabase('candidatos', params=params)
        return [item['username'] for item in items if item.get('username')]

    async def ensure_competitor_coverage(self, per_cargo=3):
        """
        Garante cobertura de concorrentes baseada em dados externos (notícias + pesquisas)
        """
        print("🔍 [TargetManager] Iniciando monitoramento eleitoral externo...")

        # Inicializa monitor eleitoral
        election_monitor = ElectionMonitor()

        # Busca dados externos e atualiza cobertura
        activated_candidates = await election_monitor.update_competitor_coverage()

        # Complementa com análise interna dos candidatos existentes
        internal_activated = self._ensure_internal_coverage(per_cargo)

        all_activated = activated_candidates + internal_activated

        if all_activated:
            print(f"✅ [TargetManager] Ativados {len(all_activated)} candidatos para monitoramento: {', '.join(all_activated[:5])}{'...' if len(all_activated) > 5 else ''}")
        else:
            print("🔎 [TargetManager] Cobertura de concorrentes já está completa.")

        return all_activated

    def _ensure_internal_coverage(self, per_cargo=3):
        """
        Método auxiliar para cobertura baseada em dados internos (fallback)
        """
        params = {
            "select": "id,username,cargo,status_monitoramento,comentarios_totais_count,seguidores",
            "order": "comentarios_totais_count.desc",
            "limit": "200"
        }
        candidates = self._fetch_supabase('candidatos', params=params)
        if not candidates:
            print("⚠️ [TargetManager] Sem candidatos disponíveis para análise interna.")
            return []

        cargos = {}
        for item in candidates:
            cargo = item.get('cargo') or 'Monitorado'
            cargos.setdefault(cargo, []).append(item)

        activated = []
        for cargo, group in cargos.items():
            # Ordena por comentários totais (maior atividade)
            sorted_group = sorted(group, key=lambda x: x.get('comentarios_totais_count', 0), reverse=True)
            top = sorted_group[:per_cargo]
            for candidate in top:
                current_status = str(candidate.get('status_monitoramento') or '').strip().lower()
                if current_status != 'ativo':
                    updated = self._update_candidate(candidate['id'], {'status_monitoramento': 'ATIVO'})
                    if updated:
                        activated.append(candidate['username'])
                        print(f"✅ [TargetManager] Ativado @{candidate['username']} ({cargo}) - análise interna.")

        return activated

    def build_dynamic_queue(self, static_targets=None, limit=30):
        queue = []
        if static_targets:
            queue.extend([t for t in static_targets if t])

        stale = self.get_stale_targets(limit=limit)
        active = self.get_high_activity_targets(limit=limit)

        for target in stale + active:
            if target and target not in queue:
                queue.append(target)

        if not queue:
            print("⚠️ [TargetManager] Queue dinâmica vazia. Usando lista de fallback manual.")
            queue = static_targets or []

        print(f"📦 [TargetManager] Montado queue dinâmico com {len(queue)} alvos.")
        return queue
