"""
PASA v49 - Instagram Worker: Orquestrador Resiliente com Adaptação Operacional (SAO)
Cascata de IAs (Groq -> Mistral -> OpenRouter) com Circuit Breaker e Autocura.
"""
import os
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.supabase_service import supabase as db

logger = logging.getLogger("InstagramWorker")

# --- Imports Resilientes: Falha silenciosa se o motor não existir ---
ScraperZyte = None
ScraperHeadless = None
ZYTE_AVAILABLE = False
HEADLESS_AVAILABLE = False

try:
    from scraper_zyte import InstagramScraperZyte as ScraperZyte
    ZYTE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Motor Zyte indisponível: {e}")

try:
    from scraper_headless import InstagramScraperHeadless as ScraperHeadless
    HEADLESS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️ Motor Playwright indisponível: {e}")


class InstagramWorker:
    def __init__(self):
        self.engine_type = "none"
        if ZYTE_AVAILABLE:
            self.engine_type = "zyte"
        elif HEADLESS_AVAILABLE:
            self.engine_type = "playwright"
        else:
            logger.error("❌ NENHUM motor de raspagem disponível!")

    def _get_active_session(self) -> Optional[Dict[str, Any]]:
        """Busca uma sessão ativa (cookies) no Supabase."""
        try:
            res = (
                db.table("worker_sessions")
                .select("id, cookies")
                .eq("plataforma", "instagram")
                .eq("status", "active")
                .order("updated_at", desc=True)
                .limit(1)
                .execute()
            )
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Erro ao buscar sessão ativa: {e}")
        return None

    def _check_auth_pause(self) -> bool:
        """Verifica se há itens pausados por falha de autenticação."""
        try:
            res = (
                db.table("fila_coleta")
                .select("id")
                .eq("status", "paused_auth_fail")
                .limit(1)
                .execute()
            )
            return len(res.data) > 0
        except Exception:
            return False

    async def _rotate_session(self, bad_session_id: str) -> Optional[Dict[str, Any]]:
        """Marca a sessão atual como falha e busca uma nova no Supabase."""
        if not bad_session_id:
            return None
            
        logger.warning(f"🔄 Rotacionando sessão. Marcando {bad_session_id} como expirada...")
        try:
            db.table("worker_sessions").update({"status": "expired"}).eq("id", bad_session_id).execute()
        except Exception:
            pass
            
        new_session = self._get_active_session()
        if new_session and new_session.get("id") != bad_session_id:
            logger.info(f"✅ Nova sessão obtida: {new_session['id']}")
            return new_session
            
        logger.error("❌ Nenhuma sessão alternativa disponível para rotação.")
        return None

    def run(self, target: str) -> bool:
        """Ponto de entrada síncrono chamado pelo local_server.py"""
        if not ZYTE_AVAILABLE and not HEADLESS_AVAILABLE:
            logger.error("❌ Tentativa de execução sem nenhum motor disponível.")
            return False

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._run_async(target))
            loop.close()
            return result
        except Exception as e:
            logger.error(f"💥 ERRO CRÍTICO: {e}")
            return False

    async def _run_async(self, target: str) -> bool:
        """Pipeline assíncrona com fallback graceful, deduplicação e adaptação SAO."""
        from core.state_manager import WorkerState
        
        # Carrega o estado evolutivo deste worker
        worker_state = WorkerState("instagram_worker")
        current_level = worker_state.level
        trust = worker_state.trust_score
        
        # 🧠 MEMÓRIA DE DEDUPLICAÇÃO: Quais posts já raspamos recentemente para este alvo?
        known_shortcodes = worker_state.get(f"{target}_shortcodes", [])
        
        logger.info(f"🧬 Worker Nível {current_level} | Trust: {trust:.1f} | Alvo: @{target} | Posts conhecidos: {len(known_shortcodes)}")
        
        session = self._get_active_session()
        cookies = session.get("cookies") if session else None

        # --- LÓGICA ADAPTATIVA POR NÍVEL ---
        zyte_disabled = os.getenv("ZYTE_DISABLED", "false") == "true"
        scraped_new_data = False
        new_posts_found = []
        
        # 1. Tentativa Zyte
        if current_level >= 2 and zyte_disabled:
            logger.info("🧠 [Veterano+] Zyte desabilitado pelo Watchdog. Pulando direto para Playwright.")
        elif ZYTE_AVAILABLE and not zyte_disabled:
            try:
                timeout = 20 if current_level >= 2 else 10
                logger.info(f"🚀 Iniciando coleta via Zyte: {target} (Timeout: {timeout}s)")
                zyte = ScraperZyte(target, max_posts=5)
                # PASSA OS SHORTCODES CONHECIDOS PARA ECONOMIZAR API
                posts = await zyte.fetch_recent_posts(external_cookies=cookies, skip_shortcodes=known_shortcodes)
                
                # Filtra posts que realmente têm comentários novos (não foram marcados como skip pelo scraper)
                new_posts_found = [p for p in posts if not p.get("is_skipped")]
                
                if new_posts_found:
                    logger.info(f"✅ Zyte: {len(new_posts_found)} posts NOVOS coletados para @{target}")
                    await self._save_posts(target, new_posts_found)
                    worker_state.record_success(items_saved=len(new_posts_found))
                    scraped_new_data = True
                else:
                    logger.info(f"✅ Zyte: Nenhum post novo para @{target}. Coleta evitada (economia de recursos).")
                    worker_state.record_success(items_saved=0)
                    # Mesmo sem posts novos, atualiza o tempo de coleta
                    try:
                        db.table("candidatos").update({
                            "last_scraped_at": datetime.now(timezone.utc).isoformat(),
                        }).eq("username", target).execute()
                    except: pass
                    return True
            except Exception as e:
                logger.warning(f"⚠️ Zyte falhou para @{target}: {e}")

        # 2. Fallback Playwright (Elite ganha poderes aqui)
        if not scraped_new_data and HEADLESS_AVAILABLE:
            logger.warning(f"⚠️ Tentando FALLBACK Playwright para @{target}...")
            try:
                max_p = 7 if current_level >= 3 else 5
                max_c = 30 if current_level >= 3 else 20
                
                headless = ScraperHeadless(target, max_posts=max_p, max_comments=max_c)
                posts = await headless.fetch_recent_posts(external_cookies=cookies)
                
                # Filtra shortcodes conhecidos
                new_posts_found = [p for p in posts if p.get("shortcode") not in known_shortcodes]
                
                # Auto-rotação de sessão (Veteranos tentam sozinhos)
                if not new_posts_found and cookies and current_level >= 2:
                    logger.warning("🧠 [Veterano+] Login Wall? Tentando rotacionar sessão...")
                    new_session = await self._rotate_session(session.get("id") if session else None)
                    if new_session:
                        new_cookies = new_session.get("cookies")
                        headless = ScraperHeadless(target, max_posts=max_p, max_comments=max_c)
                        posts = await headless.fetch_recent_posts(external_cookies=new_cookies)
                        new_posts_found = [p for p in posts if p.get("shortcode") not in known_shortcodes]

                if new_posts_found:
                    logger.info(f"✅ Playwright: {len(new_posts_found)} posts NOVOS coletados para @{target}")
                    await self._save_posts(target, new_posts_found)
                    worker_state.record_success(items_saved=len(new_posts_found))
                    scraped_new_data = True
                else:
                    logger.info(f"✅ Playwright: Nenhum post novo para @{target}.")
                    worker_state.record_success(items_saved=0)
                    try:
                        db.table("candidatos").update({
                            "last_scraped_at": datetime.now(timezone.utc).isoformat(),
                        }).eq("username", target).execute()
                    except: pass
                    return True
            except Exception as e:
                logger.error(f"💥 Playwright falhou para @{target}: {e}")
                worker_state.record_failure(reason="playwright_crash")
                return False
        
        if not scraped_new_data:
            worker_state.record_failure(reason="no_new_data")
            return True # Retorna True para não punir o worker por falta de conteúdo novo

        # 🧠 ATUALIZA A MEMÓRIA: Salva os shortcodes que raspamos (novos + antigos)
        current_shortcodes = [p.get("shortcode") for p in new_posts_found if p.get("shortcode")]
        all_shortcodes = list(set(known_shortcodes + current_shortcodes))
        # Mantém apenas os 20 mais recentes para não inflar o arquivo de estado
        worker_state.save({f"{target}_shortcodes": all_shortcodes[-20:]})
            
        return True

    async def _save_posts(self, target: str, posts: List[Dict]) -> None:
        """Salva posts e comentários no Supabase, com Quality Gate e Retry."""
        try:
            from app.workers.quality_gate import filter_comment
        except ImportError:
            filter_comment = lambda text: len(text.strip()) >= 3

        total_saved = 0
        total_rejected = 0
        
        for post in posts:
            for comment in post.get("comments", []):
                text = comment.get("text", "")
                
                if not filter_comment(text):
                    total_rejected += 1
                    continue

                comment_row = {
                    "candidato_id": target,
                    "texto_bruto": text.strip(),
                    "autor_username": comment.get("ownerUsername", "unknown"),
                    "post_shortcode": post.get("shortcode", ""),
                    "data_coleta": datetime.now(timezone.utc).isoformat(),
                    "processado_ia": False,
                    "is_hate": False,
                }
                
                # AUTOCURA: Retry de inserção no banco (3 tentativas com backoff)
                saved = False
                for attempt in range(3):
                    try:
                        db.table("comentarios").insert(comment_row).execute()
                        total_saved += 1
                        saved = True
                        break
                    except Exception as e:
                        if attempt < 2:
                            logger.warning(f"⚠️ DB Insert falhou (tentativa {attempt+1}/3). Tentando novamente em 5s...")
                            await asyncio.sleep(5 * (attempt + 1))
                        else:
                            logger.error(f"❌ Falha definitiva ao inserir comentário no banco: {e}")

        if total_saved > 0:
            logger.info(f"💾 {total_saved} salvos para @{target} (Rejeitados QG: {total_rejected})")
            try:
                db.table("candidatos").update({
                    "last_scraped_at": datetime.now(timezone.utc).isoformat(),
                }).eq("username", target).execute()
            except Exception:
                pass
