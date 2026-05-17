"""
PASA v49.7 - Instagram Worker Fortaleza
Foco: Resiliência Multi-Motor (Zyte + Playwright) e suporte a URLs diretas.
"""
import time
import random
import uuid
import re
import hashlib
from datetime import datetime, timezone
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

    def run(self, target: str):
        self.current_target = target
        if self._check_circuit_breaker():
            return False

        # 1. Identificação da Sessão e Tipo de Alvo
        is_url = target.startswith("http")
        target_username = target if not is_url else "url_source"
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
            import asyncio
            from scraper_zyte import InstagramScraperZyte
            from scraper_headless import InstagramScraperHeadless
            
            posts_data = []

            # 2. Motor Principal: Zyte API
            if is_url:
                print(f"[InstagramWorker] 🔗 Processando URL direta via ZYTE: {target}")
                zyte_scraper = InstagramScraperZyte(target_profile="url_mode")
                single_post = asyncio.run(zyte_scraper.fetch_post_comments(post_url=target, external_cookies=active_cookies))
                if single_post and single_post.get('comments'):
                    posts_data = [single_post]
            else:
                print(f"[InstagramWorker] 🚀 Iniciando coleta de PERFIL via ZYTE: {target}")
                zyte_scraper = InstagramScraperZyte(target_profile=target, max_posts=3)
                posts_data = asyncio.run(zyte_scraper.fetch_recent_posts(external_cookies=active_cookies))
            
            # 3. Fallback: Playwright (Apenas Perfil)
            if not posts_data and not is_url:
                print(f"[InstagramWorker] ⚠️ Zyte falhou. Tentando FALLBACK Playwright...")
                headless_scraper = InstagramScraperHeadless(target_profile=target, max_posts=3)
                posts_data = asyncio.run(headless_scraper.fetch_recent_posts(external_cookies=active_cookies))
            
            if not posts_data:
                print(f"[InstagramWorker] ❌ Nenhum dado retornado para {target}.")
                self.after_run(success=False, error_details="Nenhum dado retornado por Zyte/Playwright")
                return False

            # 4. Processamento e Sanitização
            all_payloads = []
            for post in posts_data:
                if post.get('text'):
                    all_payloads.append(self._sanitize_comment({
                        'text': post.get('text'),
                        'id': post.get('shortcode'),
                        'ownerUsername': target_username if not is_url else "unknown",
                        'timestamp': post.get('timestamp')
                    }, "POST"))
                
                for comment in post.get('comments', []):
                    all_payloads.append(self._sanitize_comment(comment, "COMMENT"))

            if not all_payloads:
                self.after_run(success=True, total_items=0)
                return True

            # 5. Persistência
            valid_payloads = [p for p in all_payloads if p.get('id_externo')]
            if valid_payloads:
                supabase.table('comentarios').upsert(valid_payloads, on_conflict='id_externo').execute()
                print(f"[InstagramWorker] ✅ Sucesso: {len(valid_payloads)} itens persistidos.")

            self.after_run(success=True, total_items=len(valid_payloads))
            return True

        except Exception as e:
            print(f"[InstagramWorker] 💥 ERRO CRÍTICO: {e}")
            self.after_run(success=False, error_details=str(e))
            return False

    def _scrape_section(self, target: str, section: str) -> list:
        return []
