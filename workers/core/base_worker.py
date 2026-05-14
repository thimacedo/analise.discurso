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
    def __init__(self, name: str, max_retries: int = 3, retry_base: int = 2):
        self.name = name
        self.max_retries = max_retries
        self.retry_base = retry_base
        self.logger = logging.getLogger(name)
        self.db = get_supabase_client()
        self._run_id = str(uuid4())

    # ------------------------------------------------------------------
    # Ponto de entrada público — nunca sobrescreva este método
    # ------------------------------------------------------------------
    async def execute(self, payload: dict = None) -> Any:
        started_at = datetime.now(UTC)
        self._register_run("running", payload)

        last_exc = None
        for attempt in range(1, self.max_retries + 1):
            try:
                start_time = time.time()
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
                    results=result
                )
                return result

            except Exception as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    wait = self.retry_base ** attempt  # 2s, 4s, 8s
                    self.logger.warning(
                        f"[{self.name}] Tentativa {attempt} falhou: {exc}. "
                        f"Aguardando {wait}s antes de tentar novamente..."
                    )
                    await asyncio.sleep(wait)
                else:
                    self.logger.error(
                        f"[{self.name}] Todas as {self.max_retries} tentativas "
                        f"esgotadas. Marcando como failure."
                    )

        duration_ms = int((datetime.now(UTC) - started_at).total_seconds() * 1000)
        self._finish_run(
            status="failure",
            duration_ms=duration_ms,
            error_message=str(last_exc)[:1000],
        )
        self.handle_failure(last_exc)
        
        # PASA v17: Garantia de encerramento de recursos
        try:
            await self.cleanup()
        except Exception as ce:
            self.logger.warning(f"[{self.name}] Falha no cleanup: {ce}")
            
        raise last_exc

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

    async def cleanup(self) -> None:
        """Hook opcional para limpeza de recursos ao final de cada execução."""
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
        results: list = None
    ) -> None:
        try:
            # 1. Atualiza worker_runs (O Log Histórico)
            self.db.table("worker_runs").update({
                "status":           status,
                "finished_at":      datetime.now(UTC).isoformat(),
                "duration_ms":      duration_ms,
                "items_processed":  items_processed,
                "items_rejected":   items_rejected,
                "error_message":    error_message,
            }).eq("id", self._run_id).execute()

            # 2. Lógica de Auditoria, XP e Level (O Placar de Estado)
            if status == "success":
                self._audit_and_update_state(items_processed, results)
            else:
                # Em caso de falha, apenas atualiza o status no ledger
                self.db.table("worker_ledger").update({
                    "status": "ERROR",
                    "last_audit": datetime.now(UTC).isoformat()
                }).eq("worker_name", self.name).execute()

        except Exception as exc:
            self.logger.warning(f"[{self.name}] Falha ao finalizar run: {exc}")

    def _audit_and_update_state(self, total_items: int, results: list = None) -> None:
        """
        Calcula XP, verifica Level Up e detecta burlas (neutralidade excessiva).
        Integrado de core/worker_auditor.py.
        """
        XP_PER_SUCCESS = 10
        XP_PER_CRITICAL_HIT = 25
        XP_TO_LEVEL_UP = [50, 150, 300, 600, 1000]
        
        # Busca estado atual
        res = self.db.table("worker_ledger").select("*").eq("worker_name", self.name).execute()
        ledger = res.data[0] if res.data else {"level": 0, "xp": 0, "successful_extractions": 0, "critical_hits": 0}
        
        critical_hits = 0
        neutrality_rate = 0
        if results and isinstance(results, list):
            critical_hits = sum(1 for item in results if item.get('is_hate'))
            neutral_hits = sum(1 for item in results if item.get('categoria_ia') == 'NEUTRO')
            neutrality_rate = neutral_hits / total_items if total_items > 0 else 0

        # Cálculo de XP
        xp_earned = (total_items * XP_PER_SUCCESS) + (critical_hits * XP_PER_CRITICAL_HIT)
        new_xp = ledger.get('xp', 0) + xp_earned
        current_level = ledger.get('level', 0)
        
        # Level Up
        if current_level < 5 and new_xp >= XP_TO_LEVEL_UP[current_level]:
            current_level += 1
            self.logger.info(f"🎉 LEVEL UP! {self.name} agora é Nível {current_level}!")

        # Upsert no Ledger
        self.db.table("worker_ledger").upsert({
            "worker_name": self.name,
            "xp": new_xp,
            "level": current_level,
            "successful_extractions": ledger.get('successful_extractions', 0) + total_items,
            "critical_hits": ledger.get('critical_hits', 0) + critical_hits,
            "neutrality_rate": neutrality_rate,
            "status": "ACTIVE",
            "last_audit": datetime.now(UTC).isoformat()
        }, on_conflict="worker_name").execute()
