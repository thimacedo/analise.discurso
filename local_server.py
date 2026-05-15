"""
PASA v36.1 - Sentinela Local Node: Servidor de Raspagem com Log de Operações
"""
import time
import os
import sys

# Garante que o diretório raiz do projeto esteja no Python Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
import os
import sys
from datetime import datetime
from core.supabase_service import get_supabase_client
from core.offline_cache import save_to_queue, flush_queue, load_queue
from app.workers.instagram_worker import InstagramWorker
from scripts.mass_classify import process_mass_classification
from scripts.update_threat_profiles import calculate_hate_density

# Configurações do Ciclo
CYCLE_PAUSE = 900 # 15 minutos
SCRAPE_PAUSE = 45 # Pausa entre perfis

class WarRoomUI:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def render(status: str, supabase_status: str, queue_size: int, cycle_num: int, ops_log: list):
        WarRoomUI.clear()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║         SENTINELA DEMOCRÁTICA - LOCAL NODE v36.1           ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║  Status: {status:<49}║")
        print(f"║  Supabase: {supabase_status:<48}║")
        print(f"║  Fila Offline: {queue_size:<44}║")
        print(f"║  Ciclo Atual: {cycle_num:<45}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        
        print("\n[ 📜 LOG DE OPERAÇÕES ]")
        if not ops_log:
            print("  Aguardando inicialização...")
        else:
            # Exibe os últimos 7 eventos
            for log in ops_log[-7:]:
                print(f"  {log}")
            
        print("\n [Ctrl+C] para encerrar o servidor com segurança.\n")

def log_event(ops_log: list, message: str):
    """Adiciona evento ao log com timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    ops_log.append(f"[{timestamp}] {message}")

def main_loop():
    db = get_supabase_client()
    worker = InstagramWorker()
    cycle_count = 0
    ops_log = []

    try:
        while True:
            cycle_count += 1
            log_event(ops_log, f"=== INÍCIO DO CICLO {cycle_count} ===")
            supabase_status = "🟢 ONLINE"
            
            # 1. Sincronizar Cache Offline
            WarRoomUI.render("🔄 SINCRONIZANDO", supabase_status, len(load_queue()), cycle_count, ops_log)
            try:
                synced = flush_queue(db)
                if synced > 0:
                    log_event(ops_log, f"Sincronizados {synced} itens offline com o Supabase.")
            except Exception as e:
                supabase_status = "🔴 OFFLINE"
                log_event(ops_log, f"Falha ao sincronizar cache: {str(e)[:40]}")

            # 2. Fase de Raspagem (Serial)
            WarRoomUI.render("🟡 RASPANDO INSTAGRAM", supabase_status, len(load_queue()), cycle_count, ops_log)
            try:
                pending = db.table('fila_coleta').select('id, target_id').eq('status', 'PENDENTE').eq('plataforma', 'instagram').limit(1).execute()
                
                if pending.data:
                    target = pending.data[0]['target_id']
                    item_id = pending.data[0]['id']
                    
                    db.table('fila_coleta').update({'status': 'PROCESSANDO'}).eq('id', item_id).execute()
                    log_event(ops_log, f"Iniciando raspagem de @{target}")

                    try:
                        success = worker.run(target=target)
                        new_status = 'CONCLUIDO' if success else 'FALHOU'
                        db.table('fila_coleta').update({'status': new_status}).eq('id', item_id).execute()
                        log_event(ops_log, f"Raspagem de @{target} finalizada: {new_status}")
                    except Exception as e:
                        db.table('fila_coleta').update({'status': 'FALHOU'}).eq('id', item_id).execute()
                        log_event(ops_log, f"ERRO CRÍTICO em @{target}: {str(e)[:40]}")

                    time.sleep(SCRAPE_PAUSE)
                else:
                    log_event(ops_log, "Fila de raspagem vazia.")
            except Exception as e:
                supabase_status = "🔴 OFFLINE"
                log_event(ops_log, "Erro ao acessar fila de coleta no Supabase.")

            # 3. Fase de Processamento IA (Batch)
            WarRoomUI.render("🧠 PROCESSANDO IA", supabase_status, len(load_queue()), cycle_count, ops_log)
            try:
                process_mass_classification()
                log_event(ops_log, "Lote de IA classificado com sucesso.")
            except Exception as e:
                log_event(ops_log, f"Falha no processamento de IA: {str(e)[:40]}")

            # 4. Fase de Profiling de Ameaças
            WarRoomUI.render("🎯 ATUALIZANDO AMEAÇAS", supabase_status, len(load_queue()), cycle_count, ops_log)
            try:
                calculate_hate_density()
                log_event(ops_log, "Densidade de ódio dos alvos atualizada.")
            except Exception as e:
                log_event(ops_log, f"Falha ao calcular densidade de ódio: {str(e)[:40]}")

            # 5. Sono Estratégico
            log_event(ops_log, f"Ciclo concluído. Descansando {CYCLE_PAUSE//60} min.")
            for i in range(CYCLE_PAUSE, 0, -1):
                if i % 60 == 0 or i == CYCLE_PAUSE: # Atualiza a cada minuto
                    WarRoomUI.render("🟢 AGUARDANDO PRÓXIMO CICLO", supabase_status, len(load_queue()), cycle_count, ops_log + [f"Próximo ciclo em {i//60} min..."])
                time.sleep(1)

    except KeyboardInterrupt:
        WarRoomUI.clear()
        print("\n🛑 Servidor Sentinela encerrado manualmente. Sincronizando antes de sair...")
        try:
            flush_queue(db)
        except:
            pass
        print("Concluído. Até a próxima, analista.")
        sys.exit(0)

if __name__ == "__main__":
    main_loop()
