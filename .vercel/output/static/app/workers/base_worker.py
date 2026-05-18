"""
PASA v22 - Base Worker
Fornece infraestrutura para resiliência e circuit breaker.
"""
from core.supabase_service import supabase
import logging

class BaseWorker:
    def __init__(self, platform: str = "GENERIC"):
        self.platform = platform
        self.logger = logging.getLogger(f"Worker.{platform}")

    def _check_circuit_breaker(self) -> bool:
        """Verifica se a fila da plataforma está pausada."""
        try:
            # Tenta buscar status de pausa. Se a coluna 'plataforma' não existir ainda,
            # assumimos que não está pausado para não travar o worker.
            res = supabase.table('fila_coleta')\
                .select('id')\
                .eq('status', 'paused_auth_fail')\
                .limit(1)\
                .execute()
            
            if res.data:
                print(f"🚨 [Circuit Breaker] Fila de {self.platform} pausada. Abortando run.")
                return True
        except Exception as e:
            # Se a coluna não existir, o erro será capturado aqui
            pass
        return False

    def after_run(self, success: bool, critical_hits: int = 0, rejections: int = 0, 
                  total_items: int = 0, auth_fail: bool = False, timeout: bool = False, 
                  error_details: str = None):
        """Hook de pós-execução para métricas e alertas."""
        status_str = "SUCCESS" if success else "FAILURE"
        print(f"[{self.platform}] Ciclo finalizado: {status_str}")
        print(f" -> Itens: {total_items}, Hits: {critical_hits}, Rejeições: {rejections}")
        
        if not success:
            print(f" -> Erro: {error_details}")
            if auth_fail:
                print(f" -> ⚠️ Falha de Autenticação detectada em {self.platform}!")
                # Aqui poderíamos disparar o circuit breaker no DB
