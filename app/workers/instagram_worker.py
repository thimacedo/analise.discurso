"""
PASA v22 - Instagram Worker Fortaleza
Foco: Resiliência, tratamento rigoroso de sessão e sanitização de dados.
"""
import time
import random
import uuid
from datetime import datetime
from app.workers.base_worker import BaseWorker
from core.supabase_service import supabase
from app.workers.quality_gate import is_valid_comment

class InstagramWorker(BaseWorker):
    def __init__(self):
        super().__init__(platform="instagram")
        self.worker_id = "InstagramWorker"

    def _sanitize_comment(self, raw_comment: dict, content_type: str = "POST") -> dict:
        """Garante que o dicionário de comentário mapeie EXATAMENTE para o schema do Supabase."""
        text = str(raw_comment.get('text', ''))[:2000]
        raw_id = str(raw_comment.get('id', ''))
        
        # PASA v49.3: Gera UUID determinístico (v5) a partir do ID do Instagram
        # Isso garante que o mesmo comentário sempre gere o mesmo UUID, permitindo upsert
        namespace = uuid.NAMESPACE_URL
        deterministic_uuid = str(uuid.uuid5(namespace, f"instagram.com/{raw_id}"))
        
        return {
            'id': deterministic_uuid,
            'texto_bruto': text,
            'texto_limpo': text, 
            'autor_username': str(raw_comment.get('ownerUsername', 'unknown')),
            'candidato_id': getattr(self, 'current_target', 'unknown'),
            'data_coleta': raw_comment.get('timestamp', ''),
            'plataforma': 'instagram',
            'rede_social': 'instagram',
            'processado_ia': False,
            'tipo_conteudo': content_type # PASA v47: Identifica a origem do comentário
        }

    def run(self, target: str):
        self.current_target = target
        # 1. Autocurto-circuito (Circuit Breaker)
        if self._check_circuit_breaker():
            return False

        try:
            # 2. Rate Limiting Humano (Anti-Ban)
            sleep_time = random.uniform(2.0, 6.0)
            print(f"[InstagramWorker] Dormindo {sleep_time:.2f}s para simular comportamento humano...")
            time.sleep(sleep_time)

            # 3. Execução da Raspagem (PASA v47: Posts + Reels)
            print(f"[InstagramWorker] Iniciando coleta integral para: {target}")
            
            # 3.1 Raspagem de Posts (Padrão)
            post_comments = self._scrape_section(target, "posts")
            
            # 3.2 Raspagem de Reels (PASA v47 - O Vetor Efêmero)
            reel_comments = self._scrape_section(target, "reels")

            # Consolida e salva
            all_comments = post_comments + reel_comments
            
            if not all_comments:
                print(f"[InstagramWorker] Nenhum comentário novo para {target}. Extração limpa.")
                self.after_run(success=True, critical_hits=0, rejections=0, total_items=0, auth_fail=False, timeout=False)
                return True

            # 4. Persistência
            supabase.table('comentarios').upsert(all_comments, on_conflict='id').execute()

            # 5. Pós-execução com XP
            hate_count = sum(1 for c in all_comments if "hate" in c['texto_bruto'].lower() or "ódio" in c['texto_bruto'].lower())
            
            self.after_run(
                success=True,
                critical_hits=hate_count,
                rejections=0,
                total_items=len(all_comments),
                auth_fail=False,
                timeout=False
            )
            return True

        except Exception as e:
            error_msg = str(e).lower()
            auth_fail = "login_required" in error_msg or "challenge" in error_msg or "auth" in error_msg
            timeout = "timeout" in error_msg or "timed out" in error_msg
            
            print(f"[InstagramWorker] ERRO CAPTURADO: {error_msg}")
            
            if auth_fail:
                print(f"[InstagramWorker] ⚠️ Falha de Autenticação detectada! Marcando sessão como expirada.")
                try:
                    supabase.table('worker_sessions').update({'status': 'expired'}).eq('plataforma', 'instagram').execute()
                except Exception as ex:
                    print(f"Erro ao marcar sessão como expirada: {ex}")

            self.after_run(
                success=False,
                critical_hits=0,
                rejections=0,
                total_items=0,
                auth_fail=auth_fail,
                timeout=timeout,
                error_details=str(e)
            )
            return False

    def _scrape_section(self, target: str, section: str) -> list:
        """Orquestra a raspagem de uma seção específica (posts ou reels)."""
        print(f"[InstagramWorker] Raspando seção: {section} de @{target}")
        
        # SIMULAÇÃO: No ambiente real, aqui chamaria o scraper (Apify/Playwright)
        raw_data = [
            {"id": f"ig_{section}_{random.randint(1000,9999)}", "text": f"Teste de {section} detectado", "ownerUsername": "user_test", "timestamp": datetime.now().isoformat()}
        ] if random.random() > 0.5 else []
        
        comments = []
        for rc in raw_data:
            if not is_valid_comment(rc.get('text', '')):
                continue
            
            content_type = "REEL" if section == "reels" else "POST"
            comments.append(self._sanitize_comment(rc, content_type))
            
        return comments
