
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .workers_metrics import metrics_collector

class BaseWorker(ABC):
    """
    Abstract Base Class for all Sentinel data processing workers.
    Provides a unified execution loop, standard logging, error handling, and performance metrics.
    """

    def __init__(self, name: str, batch_size: int = 50, poll_interval: int = 10):
        self.name = name
        self.batch_size = batch_size
        self.poll_interval = poll_interval
        self.logger = logging.getLogger(self.name)
        self.is_running = False
        self.metrics_collector = metrics_collector

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
        """Loop de execução unificado com captura de métricas."""
        self.is_running = True
        self.logger.info(f"🚀 Iniciando worker {self.name} (Batch: {self.batch_size}, Intervalo: {self.poll_interval}s)")

        while self.is_running:
            try:
                items = await self.fetch_pending_items(limit=self.batch_size)
                
                if items:
                    self.logger.info(f"⛏️ Processando lote de {len(items)} itens...")
                    start_time = time.time()
                    try:
                        await self.process_item_batch(items)
                        end_time = time.time()
                        
                        # Record successful execution
                        await self.metrics_collector.record_execution(
                            worker_name=self.name,
                            batch_size=self.batch_size,
                            start_time=start_time,
                            end_time=end_time,
                            items_processed=len(items),
                            success=True
                        )
                    except Exception as batch_error:
                        end_time = time.time()
                        self.logger.error(f"❌ Falha crítica ao processar o lote: {batch_error}", exc_info=True)
                        
                        # Record failed execution
                        await self.metrics_collector.record_execution(
                            worker_name=self.name,
                            batch_size=self.batch_size,
                            start_time=start_time,
                            end_time=end_time,
                            items_processed=len(items),
                            success=False,
                            error_msg=str(batch_error)
                        )
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
        """Executa um único ciclo de processamento com captura de métricas."""
        target_limit = limit or self.batch_size
        start_time = time.time()
        try:
            items = await self.fetch_pending_items(limit=target_limit)
            if items:
                await self.process_item_batch(items)
                end_time = time.time()
                
                # Record successful execution
                await self.metrics_collector.record_execution(
                    worker_name=self.name,
                    batch_size=self.batch_size,
                    start_time=start_time,
                    end_time=end_time,
                    items_processed=len(items),
                    success=True
                )
                return len(items)
            
            end_time = time.time()
            await self.metrics_collector.record_execution(
                worker_name=self.name,
                batch_size=self.batch_size,
                start_time=start_time,
                end_time=end_time,
                items_processed=0,
                success=True
            )
            return 0
        except Exception as e:
            end_time = time.time()
            self.logger.error(f"❌ Erro em run_once: {e}", exc_info=True)
            
            # Record failed execution
            await self.metrics_collector.record_execution(
                worker_name=self.name,
                batch_size=self.batch_size,
                start_time=start_time,
                end_time=end_time,
                items_processed=0,
                success=False,
                error_msg=str(e)
            )
            return 0
