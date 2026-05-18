"""
PASA v49.7 - Instagram Worker Fortaleza
Foco: Resiliência Multi-Motor (Zyte + Playwright) e suporte a URLs diretas.
"""
import time
import random
import uuid
import re
import hashlib
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
from app.workers.base_worker import BaseWorker
from core.supabase_service import supabase
from app.workers.quality_gate import is_valid_comment

class InstagramWorker(BaseWorker):
    def __init__(self):
        super().__init__(platform="instagram")
        self.worker_id = "InstagramWorker"

    def _limpar_texto(self, texto: str) -> str:
        """Remove URLs, espaços excessivos e normaliza o texto para análise."""
        if not texto: return ""
        texto = re.sub(r'http\S+', '', texto)
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto

    def _sanitize_comment(self, raw_comment: dict, content_type: str = "POST") -> dict:
        """Garante mapeamento exato para o schema do Supabase."""
        text = str(raw_comment.get('text', ''))[:2000]
        texto_limpo = self._limpar_texto(text)
        
        id_externo = str(raw_comment.get('id', ''))
        if not id_externo or id_externo == 'None':
             hash_input = f"{getattr(self, 'current_target', 'unknown')}_{content_type}_{text}"
             id_externo = f"ig_gen_{hashlib.md5(hash_input.encode()).hexdigest()[:16]}"

        namespace = uuid.NAMESPACE_URL
        id_interno = str(uuid.uuid5(namespace, f"instagram.com/{id_externo}"))
        
        return {
            'id': id_interno,
            'id_externo': id_externo,
            'texto_bruto': text,
            'texto_limpo': texto_limpo, 
            'autor_username': str(raw_comment.get('ownerUsername', 'unknown')),
            'candidato_id': getattr(self, 'current_target', 'unknown'),
            'data_coleta': raw_comment.get('timestamp') or datetime.now(timezone.utc).isoformat(),
            'plataforma': 'instagram',
            'rede_social': 'instagram',
            'processado_ia': False,
            'tipo_conteudo': content_type
        }

    async def _rotate_session(self, bad_session_id: str) -> Optional[Dict]:
        """Marca a sessão atual como falha e busca uma nova no Supabase."""
        if not bad_session_id or bad_session_id == "env_fallback":
            return None
            
        print(f"[InstagramWorker] 🔄 Rotacionando sessão. Marcando {bad_session_id} como expirada...")
        try:
            supabase.table("worker_sessions").update({"status": "expired"}).eq("id", bad_session_id).execute()
        except Exception as e:
            print(f"[InstagramWorker] Erro ao invalidar sessão: {e}")
            
        # Busca uma nova sessão
        try:
            session_res = supabase.table('worker_sessions')\
                .select('id', 'cookies')\
                .eq('plataforma', 'instagram')\
                .eq('status', 'active')\
                .neq('id', bad_session_id)\
                .order('updated_at', desc=True)\
                .limit(1)\
                .execute()
            
            if session_res.data:
                print(f"✅ Nova sessão obtida: {session_res.data[0]['id']}")
                return session_res.data[0]
        except Exception as e:
            print(f"❌ Erro ao buscar nova sessão: {e}")
            
        return None

    async def _save_posts(self, target: str, posts_data: List[Dict]) -> int:
        """Processa e salva os posts com retry na inserção do banco."""
        all_payloads = []
        target_username = target if not target.startswith("http") else "url_source"
        
        for post in posts_data:
            if post.get('text'):
                all_payloads.append(self._sanitize_comment({
                    'text': post.get('text'),
                    'id': post.get('shortcode'),
                    'ownerUsername': target_username,
                    'timestamp': post.get('timestamp')
                }, "POST"))
            
            for comment in post.get('comments', []):
                all_payloads.append(self._sanitize_comment(comment, "COMMENT"))

        if not all_payloads:
            return 0

        total_saved = 0
        for payload in all_payloads:
            # Filtro de qualidade (pode ser expandido conforme quality_gate.py)
            if not is_valid_comment(payload.get('texto_bruto', '')):
                continue
                
            # AUTOCURA: Retry de inserção no banco (3 tentativas com backoff)
            for attempt in range(3):
                try:
                    supabase.table('comentarios').upsert(payload, on_conflict='id').execute()
                    total_saved += 1
                    break
                except Exception as e:
                    if attempt < 2:
                        print(f"⚠️ DB Insert falhou (tentativa {attempt+1}/3). Tentando novamente em 5s...")
                        await asyncio.sleep(5 * (attempt + 1))
                    else:
                        print(f"❌ Falha definitiva ao inserir comentário: {e}")

        if total_saved > 0:
            print(f"[InstagramWorker] 💾 {total_saved} itens salvos para @{target}")
            try:
                supabase.table("candidatos").update({
                    "last_scraped_at": datetime.now(timezone.utc).isoformat(),
                }).eq("username", target).execute()
            except Exception:
                pass
        
        return total_saved

    def run(self, target: str):
        self.current_target = target
        if self._check_circuit_breaker():
            return False

        # 1. Identificação da Sessão
        is_url = target.startswith("http")
        active_cookies = None
        session_id = "env_fallback"
        
        try:
            session_res = supabase.table('worker_sessions')\
                .select('id', 'cookies')\
                .eq('plataforma', 'instagram')\
                .eq('status', 'active')\
                .order('updated_at', desc=True)\
                .limit(1)\
                .execute()
            
            if session_res.data:
                session_id = session_res.data[0]['id']
                active_cookies = session_res.data[0]['cookies']
                print(f"[InstagramWorker] 🔑 Usando sessão ativa: [{session_id[:8]}]")
        except Exception as e:
            print(f"[InstagramWorker] Erro ao carregar sessão: {e}")

        try:
            from scraper_zyte import InstagramScraperZyte
            from scraper_headless import InstagramScraperHeadless
            from core.scraper_weights import get_best_method, update_weight
            
            posts_data = []

            # 2. Motor Principal: Zyte API
            if is_url:
                zyte_scraper = InstagramScraperZyte(target_profile="url_mode")
                single_post = asyncio.run(zyte_scraper.fetch_post_comments(post_url=target, external_cookies=active_cookies))
                if single_post and single_post.get('comments'):
                    posts_data = [single_post]
            else:
                best = get_best_method()
                print(f"[InstagramWorker] 🚀 Coleta via X-Engine (Best: {best}): {target}")
                zyte_scraper = InstagramScraperZyte(target_profile=target, max_posts=3)
                posts_data = asyncio.run(zyte_scraper.fetch_recent_posts(external_cookies=active_cookies))
                
                if posts_data:
                    update_weight(best, True)
                else:
                    update_weight(best, False)
                    if isinstance(posts_data, dict) and posts_data.get("statusCode") == 404:
                        print(f"[ALERTA USERNAME] ❌ @{target} - 404 Not Found")
                        return False
            
            # 3. Fallback: Playwright com Auto-Rotação
            if not posts_data and not is_url:
                print(f"[InstagramWorker] ⚠️ Zyte falhou. Tentando FALLBACK Playwright...")
                headless = InstagramScraperHeadless(target, max_posts=3)
                posts_data = asyncio.run(headless.fetch_recent_posts(external_cookies=active_cookies))
                
                # AUTOCURA: Se Login Wall, tenta rotacionar sessão
                if not posts_data and active_cookies:
                    new_session = asyncio.run(self._rotate_session(session_id))
                    if new_session:
                        print(f"[InstagramWorker] 🔄 Retentando Playwright com nova sessão...")
                        posts_data = asyncio.run(headless.fetch_recent_posts(external_cookies=new_session.get('cookies')))

            if not posts_data:
                self.after_run(success=False, error_details="Nenhum dado retornado.")
                return False

            # 4. Persistência Resiliente
            total_saved = asyncio.run(self._save_posts(target, posts_data))
            self.after_run(success=True, total_items=total_saved)
            return True

        except Exception as e:
            print(f"[InstagramWorker] 💥 ERRO CRÍTICO: {e}")
            self.after_run(success=False, error_details=str(e))
            return False
