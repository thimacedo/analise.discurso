# official_solenya_daemon.py
import time
import logging
from main_orchestrator import SentinelOrchestrator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - DAEMON - %(message)s')
logger = logging.getLogger("SolenyaDaemon")

class PSR1RewardProtocol:
    """Implementação do Protocolo de Recompensas PSR-1 para os Workers."""
    @staticmethod
    def issue_reward(worker_id: str, items_processed: int, critical_flags: int):
        # A lógica real acionaria um smart contract ou atualizaria o ledger Supabase
        reward_points = (items_processed * 1) + (critical_flags * 5)
        logger.info(f"[PSR-1 TRIGGER] Reward Issued: Worker '{worker_id}' earned {reward_points} pts. (Items: {items_processed}, Critical: {critical_flags})")
        # return suabase.table("worker_rewards").insert(...)

def start_daemon(interval_minutes: int = 60, worker_id: str = "worker-natal-01"):
    targets = ["camaradenatal", "tce_rn"]
    orchestrator = SentinelOrchestrator(targets)
    
    logger.info(f"Solenya Daemon initialized. Interval: {interval_minutes}m. Worker: {worker_id}")
    
    while True:
        try:
            results = orchestrator.run_collection_cycle()
            
            # Cálculo de métricas para o PSR-1
            total_items = len(results)
            critical_items = sum(1 for r in results if r.get("pasa_classification") == "CRITICAL")
            
            # Dispara o protocolo de recompensas
            if total_items > 0:
                PSR1RewardProtocol.issue_reward(
                    worker_id=worker_id, 
                    items_processed=total_items, 
                    critical_flags=critical_items
                )
            
            logger.info(f"Sleeping for {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            logger.info("Daemon gracefully stopped by user.")
            break
        except Exception as e:
            logger.error(f"Critical daemon error: {e}")
            time.sleep(60) # Espera 1 minuto antes de tentar novamente após erro severo

if __name__ == "__main__":
    start_daemon(interval_minutes=15)