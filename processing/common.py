import asyncio
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseWorker(ABC):
    """
    Abstract Base Class for all Sentinel data processing workers.
    Provides a unified execution loop, standard logging, and error handling structure.
    """

    def __init__(self, name: str, batch_size: int = 50, poll_interval: int = 10):
        self.name = name
        self.batch_size = batch_size
        self.poll_interval = poll_interval
        self.logger = logging.getLogger(self.name)
        self.is_running = False

    @abstractmethod
    async def fetch_pending_items(self, limit: int) -> List[Dict[str, Any]]:
        """Busca itens pendentes no banco de dados."""
        pass

    @abstractmethod
    async def process_item_batch(self, items: List[Dict[str, Any]]) -> None:
        """Processa o lote de itens e atualiza o estado no banco de dados."""
        pass

    @abstractmethod
    async def handle_failure(self, item: Dict[str, Any], error: Exception) -> None:
        """Lida com falhas no processamento de um item específico."""
        pass

    async def run(self):
        """Loop de execução unificado."""
        self.is_running = True
        self.logger.info(f"🚀 Iniciando worker {self.name} (Batch: {self.batch_size}, Intervalo: {self.poll_interval}s)")

        while self.is_running:
            try:
                items = await self.fetch_pending_items(limit=self.batch_size)
                
                if items:
                    self.logger.info(f"⛏️ Processando lote de {len(items)} itens...")
                    try:
                        await self.process_item_batch(items)
                    except Exception as batch_error:
                        self.logger.error(f"❌ Falha crítica ao processar o lote: {batch_error}", exc_info=True)
                        # Depending on implementation, subclasses might handle individual errors.
                        # This catch prevents the whole worker from crashing on a batch-level exception.
                else:
                    self.logger.debug(f"💤 Nenhum item pendente. Aguardando {self.poll_interval}s...")
                    await asyncio.sleep(self.poll_interval)
            
            except Exception as fetch_error:
                self.logger.error(f"❌ Erro no loop principal (fetch_pending_items): {fetch_error}", exc_info=True)
                await asyncio.sleep(self.poll_interval) # Backoff em caso de falha de banco

    def stop(self):
        """Solicita a parada graciosa do worker."""
        self.logger.info(f"🛑 Solicitando parada do worker {self.name}...")
        self.is_running = False

    async def run_once(self, limit: int = None):
        """Executa um único ciclo de processamento."""
        target_limit = limit or self.batch_size
        try:
            items = await self.fetch_pending_items(limit=target_limit)
            if items:
                await self.process_item_batch(items)
                return len(items)
            return 0
        except Exception as e:
            self.logger.error(f"❌ Erro em run_once: {e}", exc_info=True)
            return 0
