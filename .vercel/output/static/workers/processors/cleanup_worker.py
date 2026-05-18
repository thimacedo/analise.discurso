# workers/processors/cleanup_worker.py
from __future__ import annotations
import asyncio
import sys
from datetime import datetime, UTC
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workers.core.base_worker import BaseWorker
from core.event_bus import bus
from core.supabase_service import get_supabase_client


class CleanupWorker(BaseWorker):
    def __init__(self):
        super().__init__(name="CleanupWorker", max_retries=1)
        self.db = get_supabase_client()
        self.retention_days = 7

    async def _run(self, payload: dict) -> list:
        results = []

        # 1. Remove worker_runs antigos
        try:
            res = self.db.rpc("cleanup_old_runs", {
                "p_days": self.retention_days
            }).execute()
            deleted_runs = res.data or 0
            results.append(f"worker_runs: {deleted_runs} rows deletadas")
            self.logger.info(f"🧹 worker_runs: {deleted_runs} registros removidos")
        except Exception as e:
            self.logger.warning(f"Falha ao limpar worker_runs: {e}")

        # 2. Move dead letters de todas as filas
        from core.event_bus import QUEUES
        total_dlq = 0
        for queue in QUEUES:
            killed = bus.move_dead_letters(queue, max_retries=3)
            total_dlq += killed

        results.append(f"DLQ: {total_dlq} mensagens zumbis removidas")
        self.logger.info(f"☠️  DLQ: {total_dlq} mensagens movidas")

        # 3. Remove dead_letter_queue com mais de 30 dias
        try:
            self.db.rpc("cleanup_dead_letters", {"p_days": 30}).execute()
            results.append("dead_letter_queue: limpeza concluída")
        except Exception as e:
            self.logger.warning(f"Falha ao limpar dead_letter_queue: {e}")

        return results


if __name__ == "__main__":
    asyncio.run(CleanupWorker().execute({}))
