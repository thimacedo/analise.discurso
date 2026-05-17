"""
PASA v49.3 - Instagram Worker Fortaleza
Foco: Resiliência, tratamento rigoroso de schema e persistência garantida.
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
        """
        Garante que o dicionário de comentário mapeie EXATAMENTE para o schema do Supabase.
        Inclui obrigatoriamente id_externo (NOT NULL).
        """
        text = str(raw_comment.get('text', ''))[:2000]
        texto_limpo = self._limpar_texto(text)
        
        # 1. Identifica ou gera o id_externo (ID real da rede social)
        id_externo = str(raw_comment.get('id', ''))
        if not id_externo or id_externo == 'None':
             # Fallback determinístico baseado no conteúdo para dados de teste ou incompletos
             hash_input = f"{getattr(self, 'current_target', 'unknown')}_{content_type}_{text}"
             id_externo = f"ig_gen_{hashlib.md5(hash_input.encode()).hexdigest()[:16]}"

        # 2. Gera UUID determinístico (v5) a partir do id_externo para o ID interno (PK)
        namespace = uuid.NAMESPACE_URL
        id_interno = str(uuid.uuid5(namespace, f"instagram.com/{id_externo}"))
        
        return {
            'id': id_interno,
            'id_externo': id_externo,          # ← CAMPO OBRIGATÓRIO (NOT NULL)
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
        # 1. Autocurto-circuito (Circuit Breaker)
        if self._check_circuit_breaker():
            return False

        # 1.1 Identificação da Sessão (PASA v49.6: Multi-session support)
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
                print(f"[InstagramWorker] 🔑 Usando sessão ativa do banco: [{session_id[:8]}]")
            else:
                print("[InstagramWorker] ⚠️ Nenhuma sessão ativa no banco. Usando fallback do .env.")
        except Exception as e:
            print(f"[InstagramWorker] Erro ao carregar sessão do banco: {e}")

        try:
            import asyncio
            from scraper_headless import InstagramScraperHeadless
            
            # 2. Execução da Raspagem Real via Playwright
            print(f"[InstagramWorker] 🚀 Iniciando coleta REAL para: {target}")
            scraper = InstagramScraperHeadless(target_profile=target, max_posts=3)
            
            # Executa a raspagem com os cookies da sessão ativa
            posts_data = asyncio.run(scraper.fetch_recent_posts(external_cookies=active_cookies))
            
            if not posts_data:
                print(f"[InstagramWorker] ⚠️ Nenhum dado retornado para {target}. Verifique cookies/sessão.")
                
                # Se falhou com sessão do banco, marca como expirada
                if session_id != "env_fallback":
                    try:
                        supabase.table('worker_sessions').update({'status': 'expired'}).eq('id', session_id).execute()
                        print(f"[InstagramWorker] 🚩 Sessão [{session_id[:8]}] marcada como expirada.")
                    except: pass
                
                self.after_run(success=False, total_items=0, error_details="Nenhum dado retornado")
                return False

            # 3. Processamento e Sanitização dos Comentários
            all_payloads = []
            for post in posts_data:
                # Salva o post caption
                if post.get('text'):
                    post_caption = {
                        'text': post.get('text', ''),
                        'id': post.get('shortcode', ''),
                        'ownerUsername': target,
                        'timestamp': post.get('timestamp')
                    }
                    all_payloads.append(self._sanitize_comment(post_caption, "POST"))
                
                # Adiciona comentários
                for comment in post.get('comments', []):
                    all_payloads.append(self._sanitize_comment(comment, "COMMENT"))

            if not all_payloads:
                print(f"[InstagramWorker] Nenhum comentário extraído para {target}.")
                self.after_run(success=True, total_items=0)
                return True

            # 4. Persistência
            valid_payloads = [p for p in all_payloads if p.get('id_externo')]
            if valid_payloads:
                supabase.table('comentarios').upsert(valid_payloads, on_conflict='id_externo').execute()
                print(f"[InstagramWorker] ✅ Sucesso: {len(valid_payloads)} itens reais persistidos para @{target}")

            # 5. Pós-execução
            self.after_run(
                success=True,
                total_items=len(valid_payloads)
            )
            return True

        except Exception as e:
            print(f"[InstagramWorker] 💥 ERRO CRÍTICO NA RASPAGEM: {e}")
            self.after_run(success=False, error_details=str(e))
            return False

    def _scrape_section(self, target: str, section: str) -> list:
        """Legado: Agora centralizado no método run via Playwright."""
        return []