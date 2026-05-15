"""
PASA v35 - Sentinela Local Node: Servidor de Raspagem e Processamento Serial
Modo War Room com interface de terminal e sincronização Supabase-First.
"""
import time
import os
import sys
from core.supabase_service import get_supabase_client
from core.offline_cache import save_to_queue, flush_queue, load_queue
from app.workers.instagram_worker import InstagramWorker
# classifier_engine.py contém classify_batch, mas o orquestrador pode usar o script de massa
from scripts.mass_classify import process_mass_classification

# Configurações do Ciclo
CYCLE_PAUSE = 900 # 15 minutos de sono entre ciclos completos (ajustável)
SCRAPE_PAUSE = 45 # Pausa entre perfis no mesmo ciclo

class WarRoomUI:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def render(status: str, supabase_status: str, queue_size: int, last_action: str, cycle_num: int):
        WarRoomUI.clear()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║         SENTINELA DEMOCRÁTICA - LOCAL NODE v35.0           ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║  Status: {status:<49}║")
        print(f"║  Supabase: {supabase_status:<48}║")
        print(f"║  Fila Offline: {queue_size:<44}║")
        print(f"║  Ciclo Atual: {cycle_num:<45}║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print(f"║  Última Ação: {last_action[:47]:<47}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print("\n [Ctrl+C] para encerrar o servidor com segurança.\n")

def main_loop():
    db = get_supabase_client()
    worker = InstagramWorker()
    cycle_count = 0

    try:
        while True:
            cycle_count += 1
            last_action = "Iniciando ciclo..."
            supabase_status = "🟢 ONLINE"
            
            # 1. Sincronizar Cache Offline
            WarRoomUI.render("🔄 SINCRONIZANDO", supabase_status, len(load_queue()), last_action, cycle_count)
            try:
                synced = flush_queue(db)
                last_action = f"Sincronizados {synced} itens offline."
            except Exception:
                supabase_status = "🔴 OFFLINE"

            # 2. Fase de Raspagem (Serial)
            WarRoomUI.render("🟡 RASPANDO INSTAGRAM", supabase_status, len(load_queue()), last_action, cycle_count)
            
            try:
                # Tenta pegar um alvo pendente do Supabase
                pending = db.table('fila_coleta').select('id, target_id').eq('status', 'PENDENTE').eq('plataforma', 'instagram').limit(1).execute()
                
                if pending.data:
                    target = pending.data[0]['target_id']
                    item_id = pending.data[0]['id']
                    
                    db.table('fila_coleta').update({'status': 'PROCESSANDO'}).eq('id', item_id).execute()
                    last_action = f"Raspando: @{target}"
                    WarRoomUI.render("🟡 RASPANDO INSTAGRAM", supabase_status, len(load_queue()), last_action, cycle_count)

                    try:
                        # O InstagramWorker.run geralmente recebe o target
                        success = worker.run(target=target)
                        new_status = 'CONCLUIDO' if success else 'FALHOU'
                        db.table('fila_coleta').update({'status': new_status}).eq('id', item_id).execute()
                        last_action = f"Raspagem de @{target} finalizada."
                    except Exception as e:
                        last_action = f"Erro crítico em @{target}: {str(e)[:30]}"
                        db.table('fila_coleta').update({'status': 'FALHOU'}).eq('id', item_id).execute()

                    # Pausa respirada entre perfis
                    time.sleep(SCRAPE_PAUSE)
                else:
                    last_action = "Fila de raspagem vazia."
            except Exception as e:
                supabase_status = "🔴 OFFLINE"
                last_action = "Erro ao acessar fila de coleta."

            # 3. Fase de Processamento IA (Batch)
            WarRoomUI.render("🧠 PROCESSANDO IA", supabase_status, len(load_queue()), last_action, cycle_count)
            try:
                # Roda a classificação em lote
                process_mass_classification()
                last_action += " | IA Processada."
            except Exception as e:
                last_action += f" | Falha na IA: {str(e)[:20]}"

            # 4. Sono Estratégico
            WarRoomUI.render("🟢 AGUARDANDO PRÓXIMO CICLO", supabase_status, len(load_queue()), last_action, cycle_count)
            for i in range(CYCLE_PAUSE, 0, -1):
                if i % 60 == 0: # Atualiza a cada minuto
                    WarRoomUI.render("🟢 AGUARDANDO PRÓXIMO CICLO", supabase_status, len(load_queue()), f"Próximo ciclo em {i//60} min. {last_action}", cycle_count)
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
