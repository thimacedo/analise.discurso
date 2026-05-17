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
            'tipo_conteudo': content_type,
            'confidence_score': 0,
            'evidence_extracted': None
        }

    def run(self, target: str):
        self.current_target = target
        # 1. Autocurto-circuito (Circuit Breaker)
        if self._check_circuit_breaker():
            return False

        # 1.1 Identificação da Sessão (PASA v49.6: Multi-session support)
        try:
            session_res = supabase.table('worker_sessions')\
                .select('id', 'cookies')\
                .eq('plataforma', 'instagram')\
                .eq('status', 'active')\
                .order('updated_at', desc=True)\
                .limit(1)\
                .execute()
            
            if not session_res.data:
                print("[InstagramWorker] 🛑 Erro: Nenhuma sessão ativa disponível no banco.")
                return False
                
            self.active_session_id = session_res.data[0]['id']
            self.active_cookies = session_res.data[0]['cookies']
        except Exception as e:
            print(f"[InstagramWorker] Erro ao carregar sessão: {e}")
            return False

        try:
            # 2. Rate Limiting Humano Otimizado (-25% tempo total médio)
            sleep_time = random.uniform(1.5, 3.5)
            print(f"[InstagramWorker] Sessão [{self.active_session_id[:8]}] ativa. Dormindo {sleep_time:.2f}s...")
            time.sleep(sleep_time)

            # 3. Execução da Raspagem (PASA v47: Posts + Reels)
            print(f"[InstagramWorker] Iniciando coleta integral para: {target}")
            
            # 3.1 Raspagem de Posts
            post_comments = self._scrape_section(target, "posts")
            
            # 3.2 Raspagem de Reels
            reel_comments = self._scrape_section(target, "reels")

            # Consolida e salva
            all_payloads = post_comments + reel_comments
            
            if not all_payloads:
                print(f"[InstagramWorker] Nenhum comentário novo para {target}. Extração limpa.")
                self.after_run(success=True, critical_hits=0, rejections=0, total_items=0, auth_fail=False, timeout=False)
                return True

            # 4. Persistência com Validação de Sanidade
            # Filtra payloads que porventura ainda estejam sem id_externo
            valid_payloads = [p for p in all_payloads if p.get('id_externo')]
            
            if valid_payloads:
                supabase.table('comentarios').upsert(valid_payloads, on_conflict='id_externo').execute()
                print(f"[InstagramWorker] Sucesso: {len(valid_payloads)} comentários persistidos para @{target}")

            # 5. Pós-execução com XP
            hate_count = sum(1 for c in valid_payloads if "hate" in c['texto_bruto'].lower() or "ódio" in c['texto_bruto'].lower())
            
            self.after_run(
                success=True,
                critical_hits=hate_count,
                rejections=len(all_payloads) - len(valid_payloads),
                total_items=len(valid_payloads),
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
                print(f"[InstagramWorker] ⚠️ Falha na Sessão {self.active_session_id[:8]}! Marcando como expirada.")
                try:
                    # PASA v49.6: Marca apenas a sessão que falhou
                    supabase.table('worker_sessions').update({'status': 'expired'}).eq('id', self.active_session_id).execute()
                except Exception as ex:
                    print(f"Erro ao invalidar sessão: {ex}")

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
        # Agora gerando IDs fictícios consistentes para o id_externo
        raw_data = [
            {
                "id": f"ig_{section}_{target}_{random.randint(1000,9999)}", 
                "text": f"Conteúdo de {section} detectado para @{target}", 
                "ownerUsername": "user_test", 
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ] if random.random() > 0.3 else []
        
        comments = []
        for rc in raw_data:
            texto = rc.get('text', '')
            texto_limpo = self._limpar_texto(texto)
            if not texto_limpo or not is_valid_comment(texto):
                continue
            
            content_type = "REEL" if section == "reels" else "POST"
            comments.append(self._sanitize_comment(rc, content_type))
            
        return comments