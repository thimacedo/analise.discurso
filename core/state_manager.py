"""
PASA v50 - State Manager: Motor de Persistência Atômica e Evolutiva.
Implementa checkpointing via os.replace e sistema de XP/Level (SAO).
"""
import os
import json
import time
import logging
from threading import Lock
from typing import Dict, Any, Optional

logger = logging.getLogger("StateManager")

class WorkerState:
    def __init__(self, worker_name: str):
        self.worker_name = worker_name
        self.lock = Lock()
        self.file_path = f"runtime_state/{worker_name}_state.json"
        self.temp_path = self.file_path + ".tmp"
        
        if not os.path.exists("runtime_state"):
            os.makedirs("runtime_state")
            
        self.state = self._load()

    def _load(self) -> Dict[str, Any]:
        """Carrega o estado do disco com fallback para padrão."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erro ao carregar estado {self.worker_name}: {e}")
        
        return {
            "success_count": 0,
            "failure_count": 0,
            "total_items_saved": 0,
            "last_success_at": 0,
            "last_failure_at": 0,
            "last_failure_reason": None,
            "cycle_count": 0
        }

    def save(self, data: Dict[str, Any] = None) -> None:
        """Persistência Atômica usando os.replace para evitar corrupção em crashes."""
        with self.lock:
            if data:
                self.state.update(data)
            
            try:
                with open(self.temp_path, "w", encoding="utf-8") as f:
                    json.dump(self.state, f, indent=4)
                
                # Atomic swap
                os.replace(self.temp_path, self.file_path)
            except Exception as e:
                logger.error(f"Erro ao salvar estado atômico {self.worker_name}: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        with self.lock:
            return self.state.get(key, default)

    @property
    def level(self) -> int:
        """Calcula o nível do worker baseado em métricas acumuladas (SAO)."""
        with self.lock:
            successes = self.state.get("success_count", 0)
            failures = self.state.get("failure_count", 0)
            
            total = successes + failures
            if total == 0:
                return 1
                
            success_rate = successes / total
            
            if successes >= 500 and success_rate >= 0.95:
                return 4 # Sentinela
            elif successes >= 200 and success_rate >= 0.90:
                return 3 # Elite
            elif successes >= 50 and success_rate >= 0.80:
                return 2 # Veterano
            else:
                return 1 # Recruta

    @property
    def trust_score(self) -> float:
        """Score de confiança de 0.0 a 10.0."""
        with self.lock:
            successes = self.state.get("success_count", 0)
            failures = self.state.get("failure_count", 0)
            
            total = successes + failures
            if total == 0:
                return 5.0 # Neutro
                
            rate = successes / total
            return min(10.0, rate * 10.0)

    def record_success(self, items_saved: int = 1) -> None:
        """Registra um sucesso e evolui o estado."""
        with self.lock:
            self.state["success_count"] = self.state.get("success_count", 0) + 1
            self.state["total_items_saved"] = self.state.get("total_items_saved", 0) + items_saved
            self.state["last_success_at"] = time.time()
            
            # Recompensa: Se salvou muitos itens, bonus de XP
            if items_saved > 20:
                self.state["success_count"] += 1 # XP duplo
                
            self.save() # Persiste imediatamente

    def record_failure(self, reason: str = "unknown") -> None:
        """Registra uma falha e degrada o estado."""
        with self.lock:
            self.state["failure_count"] = self.state.get("failure_count", 0) + 1
            self.state["last_failure_reason"] = reason
            self.state["last_failure_at"] = time.time()
            self.save()

    def mark_crash_recovery(self) -> Optional[str]:
        """Identifica se o último ciclo crashou e retorna o alvo pendente."""
        with self.lock:
            if self.state.get("last_operation_status") == "cycling":
                return self.state.get("current_target")
            return None
