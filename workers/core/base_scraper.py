# workers/core/base_scraper.py
from __future__ import annotations
import os
import random
import logging
from workers.core.base_worker import BaseWorker
from core.supabase_service import get_supabase_client


class BaseScraper(BaseWorker):
    """
    Extensão do BaseWorker para workers que fazem scraping.
    Adiciona: rotação de sessões, rotação de proxies, user-agent pool.
    """

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    ]

    def __init__(self, name: str, max_retries: int = 3):
        super().__init__(name=name, max_retries=max_retries)
        self.db = get_supabase_client()
        self._session: dict | None = None
        self._proxy:   str | None = None

    # ------------------------------------------------------------------
    # Sessão
    # ------------------------------------------------------------------
    def get_session(self) -> dict:
        """
        Busca uma sessão ativa do banco e marca como em uso.
        Rotaciona automaticamente se a atual estiver bloqueada.
        """
        res = (
            self.db.table("scraping_accounts")
            .select("*")
            .eq("status", "active")
            .order("last_used_at", desc=False)  # usa a menos recente
            .limit(1)
            .execute()
        )
        accounts = res.data or []

        if not accounts:
            # Fallback para variáveis de ambiente se a tabela estiver vazia (legado)
            self.logger.warning("Nenhuma conta em scraping_accounts. Usando variáveis de ambiente.")
            return {
                "session_id": os.getenv("INSTAGRAM_SESSIONID"),
                "ds_user_id": os.getenv("INSTAGRAM_DS_USER_ID"),
                "csrf_token": os.getenv("INSTAGRAM_CSRFTOKEN"),
                "username": "env_account"
            }

        account = accounts[0]
        self._session = account

        # Marca como em uso para evitar colisão com outro worker
        try:
            self.db.table("scraping_accounts").update({
                "last_used_at": datetime.now(UTC).isoformat(),
            }).eq("id", account["id"]).execute()
        except: pass

        self.logger.info(
            f"🔑 Sessão selecionada: {account.get('username', account.get('id', 'unknown'))}"
        )
        return account

    def mark_session_blocked(self) -> None:
        """Marca a sessão atual como bloqueada para que não seja reusada."""
        if not self._session or "id" not in self._session:
            return
        try:
            self.db.table("scraping_accounts").update({
                "status": "blocked",
            }).eq("id", self._session["id"]).execute()
            self.logger.warning(
                f"🚫 Sessão {self._session.get('username')} marcada como bloqueada."
            )
        except: pass
        self._session = None

    # ------------------------------------------------------------------
    # Proxy
    # ------------------------------------------------------------------
    def get_proxy(self) -> str | None:
        """
        Retorna um proxy aleatório da lista de env vars.
        Formato esperado: PROXIES=http://user:pass@host:port,http://...
        """
        raw = os.getenv("PROXIES", "")
        proxies = [p.strip() for p in raw.split(",") if p.strip()]

        if not proxies:
            self.logger.debug("Nenhum proxy configurado. Usando IP direto.")
            return None

        chosen = random.choice(proxies)
        self._proxy = chosen
        self.logger.info(f"🌐 Proxy selecionado: {chosen.split('@')[-1]}")
        return chosen

    # ------------------------------------------------------------------
    # User-Agent
    # ------------------------------------------------------------------
    def get_user_agent(self) -> str:
        return random.choice(self.USER_AGENTS)

    # ------------------------------------------------------------------
    # Cookies a partir da sessão do banco
    # ------------------------------------------------------------------
    def build_cookies(self) -> list[dict]:
        if not self._session:
            self.get_session()

        return [
            {
                "name": "sessionid",
                "value": self._session.get("session_id"),
                "domain": ".instagram.com",
                "path": "/",
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax",
            },
            {
                "name": "ds_user_id",
                "value": self._session.get("ds_user_id"),
                "domain": ".instagram.com",
                "path": "/",
                "secure": True,
            },
            {
                "name": "csrftoken",
                "value": self._session.get("csrf_token"),
                "domain": ".instagram.com",
                "path": "/",
                "secure": True,
            },
        ]
from datetime import datetime, UTC
