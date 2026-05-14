# core/event_bus.py
from __future__ import annotations
import logging
from core.supabase_service import get_supabase_client

logger = logging.getLogger("EventBus")

QUEUES = {
    "scan_candidate":    "scan_candidate",
    "scrape_profile":    "scrape_profile",
    "classify_comments": "classify_comments",
    "generate_report":   "generate_report",
}

class EventBus:
    def __init__(self):
        self.db = get_supabase_client()

    def publish(self, queue: str, payload: dict) -> None:
        try:
            # Nota: pgmq_send é a função nativa do PGMQ. 
            # Se não estiver disponível, usamos o insert simples na pg_queue.
            self.db.rpc("pgmq_send", {
                "queue_name": QUEUES.get(queue, queue),
                "msg":        payload,
            }).execute()
        except Exception as exc:
            logger.error(f"[EventBus] Falha ao publicar em '{queue}': {exc}")
            # Fallback para insert manual se RPC falhar
            try:
                self.db.table("pg_queue").insert({
                    "queue_name": QUEUES.get(queue, queue),
                    "payload": payload,
                    "status": "PENDING"
                }).execute()
            except:
                raise exc

    def consume(self, queue: str, batch_size: int = 5) -> list[dict]:
        """
        Usa a RPC com FOR UPDATE SKIP LOCKED.
        Dois workers chamando consume() ao mesmo tempo nunca
        receberão a mesma mensagem.
        """
        try:
            res = self.db.rpc("consume_messages", {
                "p_queue_name":         QUEUES.get(queue, queue),
                "p_batch_size":         batch_size,
                "p_visibility_timeout": 30,
            }).execute()
            return res.data or []
        except Exception as exc:
            logger.error(f"[EventBus] Falha ao consumir '{queue}': {exc}")
            return []

    def ack(self, queue: str, msg_id: int) -> None:
        try:
            self.db.rpc("ack_message", {
                "p_queue_name": QUEUES.get(queue, queue),
                "p_msg_id":     msg_id,
            }).execute()
        except Exception as exc:
            logger.error(f"[EventBus] Falha ao dar ack msg {msg_id}: {exc}")

    def move_dead_letters(self, queue: str, max_retries: int = 3) -> int:
        """Chama manualmente ou via CleanupWorker para drenar mensagens zumbis."""
        try:
            res = self.db.rpc("requeue_or_kill", {
                "p_queue_name":  QUEUES.get(queue, queue),
                "p_max_retries": max_retries,
            }).execute()
            killed = res.data or 0
            if killed:
                logger.warning(
                    f"[EventBus] {killed} mensagens movidas para DLQ em '{queue}'"
                )
            return killed
        except Exception as exc:
            logger.error(f"[EventBus] Falha ao mover DLQ: {exc}")
            return 0

bus = EventBus()
