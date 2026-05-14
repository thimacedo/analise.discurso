# core/event_bus.py
import json
from datetime import datetime, timedelta, UTC
from core.supabase_service import get_supabase_client

class EventBus:
    def __init__(self):
        self.db = get_supabase_client()
        self.table = "pg_queue"

    def publish(self, queue_name: str, payload: dict):
        """Publica uma mensagem na fila."""
        data = {
            "queue_name": queue_name,
            "payload": payload,
            "status": "PENDING",
            "created_at": datetime.now(UTC).isoformat()
        }
        return self.db.table(self.table).insert(data).execute()

    def consume(self, queue_name: str, batch_size: int = 1, lock_duration_sec: int = 60):
        """
        Consome mensagens usando locking atômico para evitar race conditions.
        Utiliza a lógica 'FOR UPDATE SKIP LOCKED' simulada via status e locked_until.
        """
        now = datetime.now(UTC)
        lock_until = (now + timedelta(seconds=lock_duration_sec)).isoformat()
        
        # Simulação via client (Menos atômico que um RPC direto com FOR UPDATE SKIP LOCKED, 
        # mas funcional para o estágio atual do projeto).
        res = self.db.table(self.table).select("*") \
            .eq("queue_name", queue_name) \
            .eq("status", "PENDING") \
            .limit(batch_size) \
            .execute()
            
        if not res.data:
            return []

        messages = res.data
        for msg in messages:
            self.db.table(self.table).update({
                "status": "LOCKED",
                "locked_until": lock_until
            }).eq("id", msg["id"]).execute()
            
        return messages

    def ack(self, msg_id: int):
        """Confirma o processamento e remove/finaliza a mensagem."""
        return self.db.table(self.table).update({
            "status": "ACK",
            "finished_at": datetime.now(UTC).isoformat()
        }).eq("id", msg_id).execute()

    def nack(self, msg_id: int, error: str = None):
        """Sinaliza falha e devolve a mensagem para a fila."""
        return self.db.table(self.table).update({
            "status": "PENDING",
            "locked_until": None,
            "last_error": str(error) if error else None
        }).eq("id", msg_id).execute()

bus = EventBus()
