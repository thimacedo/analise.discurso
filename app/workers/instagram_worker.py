"""
PASA v49 - Instagram Worker: Orquestrador Zyte -> Playwright Fallback
"""
import asyncio
import logging
import os
from typing import Any, Dict, List, Optional

from core.supabase_service import supabase as db
from app.workers.scraper_zyte import InstagramScraperZyte
from app.workers.scraper_headless import InstagramScraperHeadless

logger = logging.getLogger("InstagramWorker")


class InstagramWorker:
    def __init__(self):
        self.engine_type = "css_dom"  # Default

    def _get_active_session(self) -> Optional[Dict[str, Any]]:
        """Busca uma sessão ativa (cookies) no Supabase para autenticar o scraping."""
        try:
            res = db.table("worker_sessions") 
                .select("id, cookies") 
                .eq("plataforma", "instagram") 
                .eq("status", "active") 
                .order("updated_at", desc=True) 
                .limit(1) 
                .execute()
            if res.data and len(res.data) > 0:
                return res.data[0]
        except Exception as e:
            logger.error(f"Erro ao buscar sessão ativa: {e}")
        return None

    def _check_auth_pause(self) -> bool:
        """Verifica se há itens pausados por falha de autenticação."""
        try:
            res = db.table("fila_coleta") 
                .select("id") 
                .eq("status", "paused_auth_fail") 
                .limit(1) 
                .execute()
            return len(res.data) > 0
        except Exception:
            return False

    def run(self, target: str) -> bool:
        """Ponto de entrada síncrono chamado pelo local_server.py"""
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
        """Pipeline assíncrona: Zyte -> Playwright Fallback."""
        session = self._get_active_session()
        cookies = session.get("cookies") if session else None

        # 1. Tentativa Zyte
        try:
            zyte = InstagramScraperZyte(target, max_posts=5)
            posts = await zyte.fetch_recent_posts(external_cookies=cookies)
            if posts:
                logger.info(f"✅ Zyte: {len(posts)} posts coletados para @{target}")
                await self._save_posts(target, posts)
                return True
        except Exception as e:
            logger.warning(f"⚠️ Zyte falhou: {e}")

        logger.warning("⚠️ Zyte falhou. Tentando FALLBACK Playwright...")

        # 2. Fallback Playwright com injeção de cookies
        try:
            headless = InstagramScraperHeadless(target, max_posts=5, max_comments=20)
            # O fetch_recent_posts já recebe external_cookies e chama _inject_cookies internamente
            posts = await headless.fetch_recent_posts(external_cookies=cookies)
            if posts:
                logger.info(f"✅ Playwright: {len(posts)} posts coletados para @{target}")
                await self._save_posts(target, posts)
                return True
            else:
                logger.warning(f"⚠️ Playwright retornou 0 posts para @{target}")
                return False
        except Exception as e:
            logger.error(f"💥 ERRO CRÍTICO: {e}")
            return False

    async def _save_posts(self, target: str, posts: List[Dict]) -> None:
        """Salva posts e comentários no Supabase."""
        for post in posts:
            try:
                # Salva comentários
                for comment in post.get("comments", []):
                    comment_row = {
                        "candidato_id": target,
                        "texto_bruto": comment.get("text", ""),
                        "autor_username": comment.get("ownerUsername", "unknown"),
                        "post_shortcode": post.get("shortcode", ""),
                        "data_coleta": __import__("datetime").datetime.now(
                            __import__("datetime").timezone.utc
                        ).isoformat(),
                        "processado_ia": False,
                        "is_hate": False,
                    }
                    db.table("comentarios").insert(comment_row).execute()

                # Atualiza contadores do candidato
                comment_count = len(post.get("comments", []))
                db.rpc("increment_comment_count", {
                    "username": target,
                    "count": comment_count
                }).execute()

            except Exception as e:
                logger.error(f"Erro ao salvar post {post.get('shortcode')}: {e}")
