# main_runner.py
"""
Processo mestre do Sentinela.
Mantém os workers rodando, redistribui trabalho e reinicia em caso de falha.

Uso:
    python main_runner.py

Em produção (systemd, supervisord, ou screen):
    screen -dmS sentinela python main_runner.py
"""
from __future__ import annotations
import asyncio
import logging
import signal
import sys
from datetime import datetime, UTC
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.event_bus import bus
from workers.processors.classifier_worker import ClassifierWorker
from workers.processors.alert_worker import AlertWorker
from workers.processors.cleanup_worker import CleanupWorker

# Garante que a pasta de logs exista
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/runner.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("MainRunner")

# Mapa: nome da fila → classe do worker que a consome
QUEUE_WORKERS: dict[str, type] = {
    "classify_comments": ClassifierWorker,
}

# Controle de shutdown gracioso
_shutdown = asyncio.Event()


def _handle_signal(sig, frame):
    logger.info(f"Sinal {sig} recebido. Encerrando com elegância...")
    _shutdown.set()


# signal.signal não funciona bem em threads no Windows se não for no main thread
try:
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)
except ValueError:
    pass


async def process_queue(queue_name: str, WorkerClass: type) -> None:
    """Consome uma fila em loop até shutdown."""
    logger.info(f"[{queue_name}] Consumidor iniciado.")

    while not _shutdown.is_set():
        try:
            messages = bus.consume(queue_name, batch_size=5)

            if not messages:
                await asyncio.sleep(10)
                continue

            logger.info(f"[{queue_name}] {len(messages)} mensagens recebidas.")

            tasks = []
            for msg in messages:
                worker = WorkerClass()
                tasks.append(
                    _run_with_ack(worker, msg, queue_name)
                )

            await asyncio.gather(*tasks, return_exceptions=True)

        except Exception as exc:
            logger.error(
                f"[{queue_name}] Erro no loop de consumo: {exc}. "
                f"Aguardando 30s antes de retomar."
            )
            await asyncio.sleep(30)

    logger.info(f"[{queue_name}] Consumidor encerrado.")


async def _run_with_ack(worker, msg: dict, queue_name: str) -> None:
    """Executa o worker e faz ack apenas em caso de sucesso."""
    msg_id = msg.get("id") # O ID na pg_queue é UUID
    payload = msg.get("payload", {})

    try:
        await worker.execute(payload)
        bus.ack(queue_name, msg_id)
        logger.info(f"[{queue_name}] msg {msg_id} processada e confirmada.")
    except Exception as exc:
        # Não faz ack — mensagem volta para a fila após locked_until
        # O BaseWorker já tentou retries internamente.
        logger.warning(
            f"[{queue_name}] msg {msg_id} falhou após retries: {exc}. "
            f"Será reprocessada automaticamente quando o lock expirar."
        )


async def scheduled_loop(
    WorkerClass: type,
    interval_seconds: int,
    label: str,
) -> None:
    """Executa workers periódicos — não orientados a fila."""
    logger.info(f"[{label}] Loop agendado iniciado (intervalo: {interval_seconds}s).")
    while not _shutdown.is_set():
        try:
            worker = WorkerClass()
            await worker.execute({})
        except Exception as exc:
            logger.error(f"[{label}] Falha na execução agendada: {exc}")
        await asyncio.sleep(interval_seconds)


async def heartbeat() -> None:
    """Log de sinal de vida a cada 5 minutos."""
    while not _shutdown.is_set():
        logger.info(
            f"💓 Runner ativo | "
            f"{datetime.now(UTC).strftime('%H:%M:%S UTC')} | "
            f"Filas: {list(QUEUE_WORKERS.keys())}"
        )
        await asyncio.sleep(300)


async def main() -> None:
    logger.info("🚀 Sentinela Main Runner iniciando...")

    # Consumidores de fila
    consumers = [
        process_queue(queue, WorkerClass)
        for queue, WorkerClass in QUEUE_WORKERS.items()
    ]

    # Loops agendados
    schedules = [
        scheduled_loop(AlertWorker, interval_seconds=300, label="AlertWorker"),
        scheduled_loop(CleanupWorker, interval_seconds=86400, label="CleanupWorker"),
    ]

    # Adiciona o heartbeat e aguarda todos
    await asyncio.gather(
        *consumers,
        *schedules,
        heartbeat(),
    )

    logger.info("👋 Runner encerrado.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupção manual detectada.")
