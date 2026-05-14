"""
PASA v22 - Instagram Worker Fortaleza
Foco: Resiliência, tratamento rigoroso de sessão e sanitização de dados.
"""
import time
import random
from app.workers.base_worker import BaseWorker
from core.supabase_service import supabase

class InstagramWorker(BaseWorker):
    def __init__(self):
        super().__init__(platform="instagram")
        self.worker_id = "InstagramWorker"

    def _sanitize_comment(self, raw_comment: dict) -> dict:
        """Garante que o dicionário de comentário tenha apenas dados válidos e tipados."""
        return {
            'id': str(raw_comment.get('id', '')),
            'texto_bruto': str(raw_comment.get('text', ''))[:2000], # Trunca textos absurdos
            'autor_username': str(raw_comment.get('ownerUsername', 'unknown')),
            'data_coleta': raw_comment.get('timestamp', ''),
            'plataforma': 'instagram'
        }

    def run(self, target: str):
        # 1. Autocurto-circuito (Circuit Breaker)
        if self._check_circuit_breaker():
            return False

        try:
            # 2. Rate Limiting Humano (Anti-Ban)
            sleep_time = random.uniform(2.0, 6.0)
            print(f"[InstagramWorker] Dormindo {sleep_time:.2f}s para simular comportamento humano...")
            time.sleep(sleep_time)

            # 3. Execução do Scraper (Simulação do fluxo Apify/Playwright real)
            print(f"[InstagramWorker] Iniciando coleta para: {target}")
            
            # SIMULAÇÃO: Troque isto pela lógica real de scraping
            resultado_scrape = random.choice([
                {"status": "success", "comments": [{"id": f"ig_{random.randint(1000,9999)}", "text": "Ok", "ownerUsername": "user1"}, {"id": f"ig_{random.randint(1000,9999)}", "text": "Hate detected", "ownerUsername": "user2"}]},
                {"status": "auth_fail", "error": "login_required"},
                {"status": "success", "comments": []} # Perfil vazio
            ])

            if resultado_scrape["status"] == "auth_fail":
                raise Exception("login_required")

            # 4. Sanitização e Persistência em Massa
            raw_comments = resultado_scrape.get("comments", [])
            if not raw_comments:
                print(f"[InstagramWorker] Nenhum comentário novo para {target}. Extração limpa.")
                self.after_run(success=True, critical_hits=0, rejections=0, total_items=0, auth_fail=False, timeout=False)
                return True

            comments_to_insert = []
            hate_count = 0
            rejected_count = 0

            for rc in raw_comments:
                if not rc.get('id') or not rc.get('text'):
                    rejected_count += 1
                    continue
                
                sanitized = self._sanitize_comment(rc)
                comments_to_insert.append(sanitized)
                
                # Detecção de "Critical Hit" simples (antes da IA classificar)
                if "hate" in sanitized['texto_bruto'].lower():
                    hate_count += 1

            # Batch Insert (Upsert)
            if comments_to_insert:
                # Nota: Certifique-se que o schema de 'comentarios' bate com as chaves
                supabase.table('comentarios').upsert(comments_to_insert, on_conflict='id').execute()

            # 5. Pós-execução com XP e Alertas
            self.after_run(
                success=True,
                critical_hits=hate_count,
                rejections=rejected_count,
                total_items=len(raw_comments),
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
