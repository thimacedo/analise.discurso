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
from workers.core.xp_engine import calculate_run_xp
from core.alert_manager import send_critical_alert

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


class BaseWorker(ABC):
    def __init__(self, name: str, platform: str = "GENERIC", max_retries: int = 3, retry_base: int = 2):
        self.name = name
        self.platform = platform
        self.max_retries = max_retries
        self.retry_base = retry_base
        self.logger = logging.getLogger(name)
        self.db = get_supabase_client()
        self._run_id = str(uuid4())

    def _check_circuit_breaker(self) -> bool:
        """Verifica se a fila da plataforma está pausada por falha de auth."""
        try:
            paused = self.db.table('fila_coleta')\
                .select('id')\
                .eq('plataforma', self.platform)\
                .eq('status', 'paused_auth_fail')\
                .limit(1)\
                .execute()
            
            if paused.data:
                self.logger.warning(f"🚨 [Circuit Breaker] Fila de {self.platform} pausada. Abortando run para preservar XP.")
                return True
        except Exception as e:
            self.logger.error(f"⚠️ Erro ao verificar Circuit Breaker: {e}")
        return False

    def _trigger_circuit_breaker(self):
        """Pausa toda a fila da plataforma para evitar falhas em cascata."""
        try:
            self.db.table('fila_coleta')\
                .update({'status': 'paused_auth_fail'})\
                .eq('plataforma', self.platform)\
                .eq('status', 'PENDENTE')\
                .execute()
            self.logger.error(f"🔥 [Circuit Breaker] Fila de {self.platform} pausada automaticamente por falha de auth.")
        except Exception as e:
            self.logger.error(f"⚠️ Erro ao disparar Circuit Breaker: {e}")

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

                await self._finish_run(
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
        await self._finish_run(
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

    async def _finish_run(
        self,
        status: str,
        duration_ms: int,
        items_processed: int = 0,
        items_rejected: int = 0,
        error_message: str = None,
        results: list = None
    ) -> None:
        try:
            # 1. Calcula XP da execução
            is_success = status == "success"
            critical_hits = 0
            if results and isinstance(results, list):
                critical_hits = sum(1 for item in results if item.get('is_hate'))

            run_xp = calculate_run_xp(
                success=is_success,
                critical_hits=critical_hits,
                rejections=items_rejected,
                total_items=items_processed + items_rejected,
                auth_fail="Auth" in (error_message or ""),
                timeout="timeout" in (error_message or "").lower()
            )

            # 2. Atualiza worker_runs (O Log Histórico)
            self.db.table("worker_runs").update({
                "status":           status,
                "finished_at":      datetime.now(UTC).isoformat(),
                "duration_ms":      duration_ms,
                "items_processed":  items_processed,
                "items_rejected":   items_rejected,
                "error_message":    error_message,
                "xp_gained":        run_xp
            }).eq("id", self._run_id).execute()

            # 3. Lógica de Auditoria, XP e Level (O Placar de Estado)
            if is_success:
                self._audit_and_update_state(items_processed, critical_hits, run_xp, results)
            else:
                # Em caso de falha, atualiza o ledger com a penalidade e status
                self._audit_and_update_state(0, 0, run_xp, None, status="ERROR")
                
                # 3.1 PASA v19: Circuit Breaker - Pausa a fila se a sessão caiu
                auth_fail = "Auth" in (error_message or "")
                if auth_fail:
                    self._trigger_circuit_breaker()
                
            # 4. PASA v18: Dispara alerta crítico se houver penalidade severa
            await send_critical_alert(
                worker_id=self.name, 
                run_xp=run_xp, 
                error_details=error_message or "Falha desconhecida"
            )

        except Exception as exc:
            self.logger.warning(f"[{self.name}] Falha ao finalizar run: {exc}")

    def _audit_and_update_state(
        self, 
        total_items: int, 
        critical_hits: int, 
        xp_earned: int, 
        results: list = None,
        status: str = "ACTIVE"
    ) -> None:
        """
        Atualiza o Ledger acumulativo do worker.
        """
        # Busca estado atual
        res = self.db.table("worker_ledger").select("*").eq("worker_name", self.name).execute()
        ledger = res.data[0] if res.data else {"xp": 0, "successful_extractions": 0, "critical_hits": 0, "total_runs": 0}
        
        neutrality_rate = 0
        if results and isinstance(results, list) and total_items > 0:
            neutral_hits = sum(1 for item in results if item.get('categoria_ia') == 'NEUTRO')
            neutrality_rate = neutral_hits / total_items

        new_xp = max(0, (ledger.get('xp') or ledger.get('current_xp') or 0) + xp_earned)
        
        # Upsert no Ledger (Trigger SQL cuida do Level)
        self.db.table("worker_ledger").upsert({
            "worker_name": self.name,
            "current_xp": new_xp,
            "successful_extractions": (ledger.get('successful_extractions') or 0) + total_items,
            "critical_hits": (ledger.get('critical_hits') or 0) + critical_hits,
            "neutrality_rate": neutrality_rate,
            "total_runs": (ledger.get('total_runs') or 0) + 1,
            "status": status,
            "last_audit": datetime.now(UTC).isoformat()
        }, on_conflict="worker_name").execute()
