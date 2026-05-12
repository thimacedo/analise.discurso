"""
Worker: SearchWatcher (Monitor de Novos Arquivos de Pesquisa)
Finalidade: Monitorar a pasta bases_pesquisas diariamente e disparar o CandidateScanner.
Protocolo Diamond: Herda de BaseWorker.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import asyncio
import hashlib
import sys
from pathlib import Path
from datetime import datetime, UTC
from typing import Set

# Ajuste dinâmico de path para o root do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from workers.core.base_worker import BaseWorker
from core.supabase_service import get_supabase_client

class SearchWatcherWorker(BaseWorker):
    def __init__(self):
        super().__init__("SearchWatcher")
        self.base_path = PROJECT_ROOT / "bases_pesquisas"
        self.processed_table = "pesquisas_processadas"
        self.scan_script = PROJECT_ROOT / "workers" / "processors" / "candidate_scanner.py"
        # Tenta usar o python atual
        self.python_exe = sys.executable or "python"

    async def _run(self, *args, **kwargs):
        """
        Executa a verificação diária.
        Args:
            *args: Argumentos posicionais.
            **kwargs: Argumentos nomeados.
        Returns:
            None
        """
        self.logger.info("🕒 Iniciando verificação diária de novas pesquisas...")
        
        try:
            # 1. Lista arquivos PDF na pasta
            current_files = list(self.base_path.glob("*.pdf"))
            new_files_found = False

            for file_path in current_files:
                # Calcula hash para verificar se é realmente novo (baseado no conteúdo)
                file_content = file_path.read_bytes()
                file_hash = hashlib.sha256(file_content).hexdigest()

                # Consulta o DB
                existing = db_client.client.table(self.processed_table)\
                    .select("id")\
                    .eq("hash_sha256", file_hash)\
                    .execute()

                if not existing.data:
                    self.logger.info(f"🆕 Novo arquivo detectado: {file_path.name}")
                    new_files_found = True
                    break # Um novo arquivo já é suficiente para disparar o scanner completo

            # 2. Se houver novos arquivos, dispara o CandidateScanner
            if new_files_found:
                self.logger.info("🚀 Disparando CandidateScanner para processar novos alvos...")
                process = await asyncio.create_subprocess_exec(
                    str(self.python_exe), str(self.scan_script),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                
                if process.returncode == 0:
                    self.logger.info("✅ CandidateScanner executado com sucesso.")
                else:
                    self.logger.error(f"❌ Falha no CandidateScanner (Code {process.returncode}): {stderr.decode()}")
            else:
                self.logger.info("✅ Nenhuma pesquisa nova encontrada hoje.")

        except Exception as e:
            self.logger.error(f"❌ Erro na rotina de monitoramento: {e}")
            with open("error.log", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] SearchWatcher Error: {str(e)}\n")

if __name__ == "__main__":
    worker = SearchWatcherWorker()
    asyncio.run(worker.execute())
