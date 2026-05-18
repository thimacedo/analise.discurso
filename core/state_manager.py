"""
PASA v49 - State Manager: Checkpointing Atômico para Workers
Garante resiliência a OOM/Crashes salvando o estado em disco de forma leve e segura.
"""
import json
import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("StateManager")

class WorkerState:
    def __init__(self, worker_name: str, state_dir: str = "runtime_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.file_path = self.state_dir / f"{worker_name}_state.json"
        self.temp_path = self.state_dir / f"{worker_name}_state.tmp"
        self.state: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Carrega o último estado salvo do disco."""
        if self.file_path.exists():
            try:
                content = self.file_path.read_text(encoding='utf-8')
                if content.strip():
                    return json.loads(content)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"⚠️ Estado de {self.file_path.name} corrompido ou inacessível: {e}. Resetando.")
        return {}

    def save(self, updates: Dict[str, Any]) -> None:
        """Atualiza o estado em memória e persiste em disco atomicamente."""
        self.state.update(updates)
        try:
            # 1. Escreve em um arquivo temporário (não afeta o arquivo principal se crashar aqui)
            json_str = json.dumps(self.state, ensure_ascii=False, separators=(',', ':')) # Compacto
            self.temp_path.write_text(json_str, encoding='utf-8')
            
            # 2. Substitui o arquivo principal atomicamente (os.replace é à prova de falhas no Windows/Linux)
            os.replace(self.temp_path, self.file_path)
        except Exception as e:
            logger.error(f"❌ Falha crítica ao salvar estado: {e}")

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Obtém um valor do estado atual."""
        return self.state.get(key, default)

    def clear(self) -> None:
        """Limpa o estado (reset forçado)."""
        self.state = {}
        try:
            if self.file_path.exists():
                self.file_path.unlink()
        except Exception:
            pass

    def mark_crash_recovery(self) -> Optional[str]:
        """
        Verifica se a última sessão terminou anormalmente (sem flag de 'finished').
        Retorna o alvo que causou a queda, se houver.
        """
        status = self.get("last_operation_status")
        target = self.get("current_target")
        
        if status == "processing" and target:
            logger.warning(f"🚨 Recuperação de Crash detectada! O sistema caiu processando: @{target}")
            # Marca como recuperado para não tentar processar esse imediatamente de novo (pode causar OOM denovo)
            self.save({"last_operation_status": "crash_recovered", "skip_target": target})
            return target
        return None
