"""
PASA v49 - Circuit Breaker para APIs de IA
Impede loops infinitos em falhas de autenticação (401) ou Rate Limit (429).
"""
import time
import logging
from typing import Dict

logger = logging.getLogger("CircuitBreaker")

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 300):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failures: Dict[str, int] = {}
        self.open_until: Dict[str, float] = {}

    def can_execute(self, service_name: str) -> bool:
        """Verifica se o circuito está aberto (bloqueado) para o serviço."""
        if service_name in self.open_until:
            if time.time() < self.open_until[service_name]:
                return False  # Circuito aberto, não executar
            else:
                # Cooldown passou, tentar novamente (half-open)
                del self.open_until[service_name]
                self.failures[service_name] = 0
                logger.info(f"🔄 [CB] Circuito HALF-OPEN para {service_name}. Tentando novamente...")
        return True

    def record_success(self, service_name: str):
        """Registra sucesso e reseta contadores."""
        self.failures.pop(service_name, None)
        self.open_until.pop(service_name, None)

    def record_failure(self, service_name: str, status_code: int = None):
        """Registra falha e abre o circuito se o limite for atingido."""
        self.failures[service_name] = self.failures.get(service_name, 0) + 1
        count = self.failures[service_name]

        # Falhas fatais (401, 403) abrem o circuito imediatamente
        if status_code in [401, 403]:
            logger.error(f"🔴 [CB] Falha FATAL ({status_code}) em {service_name}. Circuito ABERTO por 1 hora.")
            self.open_until[service_name] = time.time() + 3600  # 1 hora de bloqueio
            return

        # Falhas de limite (429) abrem o circuito com cooldown
        if status_code == 429:
            logger.warning(f"🟡 [CB] Rate Limit (429) em {service_name}. Circuito ABERTO por {self.cooldown_seconds}s.")
            self.open_until[service_name] = time.time() + self.cooldown_seconds
            return

        # Falhas normais (ex: timeout, 500) acumulam
        if count >= self.failure_threshold:
            logger.warning(f"🟠 [CB] {service_name} falhou {count}x seguidas. Circuito ABERTO por {self.cooldown_seconds}s.")
            self.open_until[service_name] = time.time() + self.cooldown_seconds

# Instância global do Circuit Breaker
ai_circuit_breaker = CircuitBreaker(failure_threshold=3, cooldown_seconds=300)
