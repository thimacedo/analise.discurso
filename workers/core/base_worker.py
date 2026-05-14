# workers/core/base_worker.py
from __future__ import annotations
from abc import ABC, abstractmethod
import asyncio
import logging
import sys
import time
from datetime import datetime, UTC
from typing import Any
from uuid import uuid4

from core.schemas import CommentPayload
from core.supabase_service import get_supabase_client

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class BaseWorker(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(name)
        self.db = get_supabase_client()
        self._run_id = str(uuid4())

    # ------------------------------------------------------------------
    # Ponto de entrada público — nunca sobrescreva este método
    # ------------------------------------------------------------------
    async def execute(self, payload: dict = None) -> Any:
        started_at = datetime.now(UTC)
        start_time = time.time()
        
        self._register_run("running", payload)

        try:
            result = await self._run(payload or {})

            duration_ms = int((time.time() - start_time) * 1000)
            
            # Tenta inferir a contagem de itens processados do resultado
            items_processed = 0
            if hasattr(result, "__len__"):
                items_processed = len(result)
            elif isinstance(result, list):
                items_processed = len(result)

            self._finish_run(
                status="success",
                duration_ms=duration_ms,
                items_processed=items_processed,
            )
            return result

        except Exception as exc:
            duration_ms = int((time.time() - start_time) * 1000)
            self._finish_run(
                status="failure",
                duration_ms=duration_ms,
                error_message=str(exc)[:1000],
            )
            self.logger.error(f"[{self.name}] Falha: {exc}", exc_info=True)
            raise

    # ------------------------------------------------------------------
    # Validação de comentários — use dentro do _run de qualquer scraper
    # ------------------------------------------------------------------
    def validate_comments(self, raw_list: list[dict]) -> tuple[list[dict], int]:
        """
        Recebe lista de dicts crus, retorna (válidos, n_rejeitados).
        Loga cada rejeição com o motivo.
        """
        valid, rejected = [], 0
        for raw in raw_list:
            # Garante que o worker_name esteja presente para o schema
            raw["worker_name"] = self.name
            try:
                validated = CommentPayload(**raw)
                valid.append(validated.model_dump())
            except Exception as exc:
                rejected += 1
                self.logger.warning(f"[{self.name}] Comentário rejeitado: {exc}")
        return valid, rejected

    # ------------------------------------------------------------------
    # Interface obrigatória
    # ------------------------------------------------------------------
    @abstractmethod
    async def _run(self, payload: dict) -> Any:
        """Lógica de negócio. Deve retornar um objeto com __len__ ou None."""
        pass

    def handle_failure(self, exception: Exception) -> None:
        """Hook opcional para alertas externos (Slack, e-mail, etc.)."""
        pass

    # ------------------------------------------------------------------
    # Internos — registro no worker_runs
    # ------------------------------------------------------------------
    def _register_run(self, status: str, payload: dict = None) -> None:
        try:
            self.db.table("worker_runs").insert({
                "id":               self._run_id,
                "worker_name":      self.name,
                "status":           status,
                "payload_snapshot": payload,
                "started_at":       datetime.now(UTC).isoformat(),
            }).execute()
        except Exception as exc:
            self.logger.warning(f"[{self.name}] Falha ao registrar run: {exc}")

    def _finish_run(
        self,
        status: str,
        duration_ms: int,
        items_processed: int = 0,
        items_rejected: int = 0,
        error_message: str = None,
    ) -> None:
        try:
            self.db.table("worker_runs").update({
                "status":           status,
                "finished_at":      datetime.now(UTC).isoformat(),
                "duration_ms":      duration_ms,
                "items_processed":  items_processed,
                "items_rejected":   items_rejected,
                "error_message":    error_message,
            }).eq("id", self._run_id).execute()

            # Atualiza o snapshot de estado atual no worker_ledger
            # Nota: Isso assume que audit_worker_result ou similar cuida de XP/Level
            self.db.table("worker_ledger").upsert({
                "worker_name":          self.name,
                "status":               "ACTIVE" if status == "success" else "ERROR",
                "last_audit":           datetime.now(UTC).isoformat(),
            }, on_conflict="worker_name").execute()

        except Exception as exc:
            self.logger.warning(f"[{self.name}] Falha ao finalizar run: {exc}")
