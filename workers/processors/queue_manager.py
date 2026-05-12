"""
Worker: QueueManager (Cérebro da Fila de Coleta)
Finalidade: Gerenciar a fila_coleta diária, garantindo rotação ponderada e atualização de todos os alvos.
Protocolo Diamond: Herda de BaseWorker.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import sys
from datetime import datetime, UTC, timedelta
from pathlib import Path
from typing import List, Dict

# Ajuste dinâmico de path para o root do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workers.core.base_worker import BaseWorker
from core.db import db_client

class QueueManagerWorker(BaseWorker):
    def __init__(self):
        super().__init__("QueueManager")
        self.batch_size = 50 # Quantos alvos agendar por ciclo

    async def _run(self, *args, **kwargs):
        self.logger.info("🧠 Gerenciando fila de alvos para o ciclo atual...")
        
        # 1. Limpa entradas antigas da fila (mais de 24h e concluídas/falhas)
        self._cleanup_old_queue()

        # 2. Busca alvos pendentes para agendamento
        # Lógica de Rotação Ponderada:
        # - Prioridade alta (P5, P4) deve aparecer mais vezes.
        # - Alvos nunca raspados (last_scraped_at IS NULL) têm prioridade absoluta.
        # - Alvos antigos (last_scraped_at ASC) vêm em seguida.
        
        targets = self._get_next_targets_to_schedule()
        
        if not targets:
            self.logger.info("✅ Todos os alvos estão atualizados na fila.")
            return

        # 3. Insere na fila_coleta
        self._schedule_targets(targets)

    def _cleanup_old_queue(self):
        """Remove registros antigos da fila para manter o banco leve."""
        yesterday = (datetime.now(UTC) - timedelta(days=1)).date().isoformat()
        try:
            db_client.client.table('fila_coleta')\
                .delete()\
                .lt('data_agendada', yesterday)\
                .execute()
            self.logger.info("🧹 Limpeza de fila antiga concluída.")
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao limpar fila: {e}")

    def _get_next_targets_to_schedule(self) -> List[Dict]:
        """Busca alvos no banco usando lógica de prioridade e frescor de dados."""
        # Query: Alvos que NÃO estão na fila de hoje com status PENDENTE ou EM_CURSO
        today = datetime.now(UTC).date().isoformat()
        
        try:
            # Pegamos os nomes de quem já está na fila hoje para evitar duplicidade
            res_current = db_client.client.table('fila_coleta')\
                .select('candidato_id')\
                .eq('data_agendada', today)\
                .execute()
            already_queued = [item['candidato_id'] for item in res_current.data]

            # Busca candidatos prioritários e esquecidos
            # Ordenação: prioridade DESC, last_scraped_at ASC
            res_candidates = db_client.client.table('candidatos')\
                .select('username, prioridade_coleta, last_scraped_at')\
                .order('prioridade_coleta', desc=True)\
                .order('last_scraped_at', desc=False)\
                .limit(200)\
                .execute()
            
            candidates = res_candidates.data
            to_queue = []
            
            for c in candidates:
                if c['username'] not in already_queued:
                    to_queue.append(c)
                if len(to_queue) >= self.batch_size:
                    break
            
            return to_queue
        except Exception as e:
            self.logger.error(f"❌ Erro ao buscar alvos: {e}")
            return []

    def _schedule_targets(self, targets: List[Dict]):
        """Insere os alvos na tabela fila_coleta."""
        today = datetime.now(UTC).date().isoformat()
        scheduled_count = 0
        
        for t in targets:
            try:
                db_client.client.table('fila_coleta').upsert({
                    "candidato_id": t['username'],
                    "prioridade": t.get('prioridade_coleta', 1),
                    "status": "PENDENTE",
                    "data_agendada": today,
                    "updated_at": datetime.now(UTC).isoformat()
                }, on_conflict="candidato_id,data_agendada").execute()
                scheduled_count += 1
            except Exception as e:
                self.logger.warning(f"⚠️ Falha ao agendar @{t['username']}: {e}")
        
        self.logger.info(f"🚀 {scheduled_count} novos alvos agendados na fila para hoje.")

if __name__ == "__main__":
    worker = QueueManagerWorker()
    asyncio.run(worker.execute())
