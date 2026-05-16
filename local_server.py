"""
PASA v44 - Sentinela Local Node: Master Server (Audit Edition)
Unifica Fila Inteligente, Cooldown Dinâmico, Monitor de Ameaças, Descanso Produtivo e Auditoria Anti-Alucinação.
"""
import time
import subprocess
import os
import sys
import logging
import asyncio
from datetime import datetime, timezone

# Ajuste de path para encontrar core e scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'workers'))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts'))

try:
    from core.db import db_client as db
    from workers.scrapers.instagram_scraper import InstagramScraper
    from scripts.update_threat_profiles import calculate_hate_density
    from scripts.mass_classify import process_mass_classification
    from workers.audit_worker import run_audit
    from scripts.check_drift import check_category_drift
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format='%(asctime)s - SERVER - %(message)s')
logger = logging.getLogger("SentinelaServer")

# Configurações do Ciclo
CYCLE_PAUSE = 900
SCRAPE_PAUSE = 45
COOLDOWN_HOURS = 6

class WarRoomUI:
    @staticmethod
    def render(status, db_status, queue_size, cycle, logs):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*75)
        print(f" SENTINELA DEMOCRÁTICA | WAR ROOM | {datetime.now().strftime('%H:%M:%S')}")
        print("="*75)
        print(f" STATUS: {status}")
        print(f" DB: {db_status} | FILA: {queue_size} | CICLO: {cycle}")
        print("-"*75)
        print(" LOGS DE OPERAÇÃO RECENTES:")
        for log in logs[-8:]:
            print(f" > {log}")
        print("="*75)
        print(" [PASA v44] Audit Edition - Integridade Forense e Anti-Alucinação")
        print("="*75)

def log_event(log_list, msg):
    log_list.append(f"[{datetime.now().strftime('%H:%M')}] {msg}")
    logger.info(msg)

async def run_server():
    try:
        worker = InstagramScraper("init")
    except Exception as e:
        logger.error(f"Erro ao inicializar worker: {e}")
        return

    cycle_count = 0
    ops_log = []

    print("\n" + "="*60)
    print("📊 DICA: Abra no navegador o painel de inspeção local:")
    print("file:///" + os.path.abspath("local_dashboard.html").replace("\\", "/"))
    print("="*60 + "\n")
    
    while True:
        cycle_count += 1
        supabase_status = "🟢 ONLINE" if db.client else "🔴 OFFLINE"
        log_event(ops_log, f"Iniciando ciclo #{cycle_count}")
        
        # 1. Fase de Raspagem Inteligente
        PROFILES_PER_CYCLE = 5
        profiles_scraped_this_cycle = 0
        
        while profiles_scraped_this_cycle < PROFILES_PER_CYCLE:
            try:
                res_pend = db.client.table('fila_coleta').select('id', count='exact').eq('status', 'PENDENTE').execute()
                queue_size = res_pend.count if res_pend.count is not None else 0
                
                WarRoomUI.render(f"🟡 RASPAGEM: ALVO {profiles_scraped_this_cycle+1}/{PROFILES_PER_CYCLE}", supabase_status, queue_size, cycle_count, ops_log)
                
                pending = db.client.table('fila_coleta').select('id, target_id').eq('status', 'PENDENTE').limit(10).execute()
                
                if not pending.data: break

                target_item = None
                for p in pending.data:
                    target_id = p['target_id']
                    cand = db.client.table('candidatos').select('last_scraped_at').eq('username', target_id).execute()
                    
                    if cand.data and cand.data[0].get('last_scraped_at'):
                        last_scraped_str = cand.data[0]['last_scraped_at']
                        try:
                            last_scraped = datetime.fromisoformat(last_scraped_str.replace('Z', '+00:00'))
                            if (datetime.now(timezone.utc) - last_scraped).total_seconds() / 3600 < COOLDOWN_HOURS:
                                db.client.table('fila_coleta').update({'status': 'CONCLUIDO'}).eq('id', p['id']).execute()
                                continue
                        except Exception: pass
                    
                    target_item = p
                    break
                
                if not target_item: break

                target_id = target_item['target_id']
                db.client.table('fila_coleta').update({'status': 'PROCESSANDO'}).eq('id', target_item['id']).execute()
                
                try:
                    worker.target_profile = target_id
                    posts = worker.fetch_recent_posts()
                    for post in posts:
                        comments = worker.fetch_comments(post['shortcode'])
                        if comments: db.client.table('comentarios').upsert(comments).execute()
                    
                    db.client.table('fila_coleta').update({'status': 'CONCLUIDO'}).eq('id', target_item['id']).execute()
                    db.client.table('candidatos').update({'last_scraped_at': datetime.now(timezone.utc).isoformat()}).eq('username', target_id).execute()
                    log_event(ops_log, f"@{target_id} concluído.")
                    profiles_scraped_this_cycle += 1
                except Exception as e:
                    db.client.table('fila_coleta').update({'status': 'FALHOU'}).eq('id', target_item['id']).execute()
                    log_event(ops_log, f"Falha em @{target_id}: {str(e)[:40]}")

                time.sleep(SCRAPE_PAUSE)
            except Exception: break

        # 2. Profiling e Git Sync
        WarRoomUI.render("📊 ATUALIZANDO PROFILER", supabase_status, "---", cycle_count, ops_log)
        try:
            calculate_hate_density()
            subprocess.run(['git', 'add', 'docs/profiler_stream.json', 'docs/kpis.json'], capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'data: atualizar monitor de ameacas (PASA v44)'], capture_output=True)
            log_event(ops_log, "Frontend sincronizado.")
        except Exception: pass

        # 3. Descanso Produtivo e IA (Otimizado PASA v45)
        rest_end_time = time.time() + CYCLE_PAUSE
        audit_done_this_rest = False
        
        while time.time() < rest_end_time:
            try:
                res_ia = db.client.table('comentarios').select('id', count='exact').eq('processado_ia', False).limit(1).execute()
                pending_ia = res_ia.count if res_ia.count is not None else 0
                
                if pending_ia > 0:
                    WarRoomUI.render(f"🧠 IA EM FUNDO: {pending_ia} PENDENTES", supabase_status, "Zzz", cycle_count, ops_log)
                    await process_mass_classification(limit=50)
                    time.sleep(10)
                else:
                    # 4. Auditoria e Deriva (PASA v45 - Apenas 1x por ciclo de descanso)
                    if not audit_done_this_rest:
                        WarRoomUI.render("🔍 AUDITORIA CRUZADA", supabase_status, "CHECKING", cycle_count, ops_log)
                        try:
                            # Tenta validar colunas antes de rodar
                            from scripts.db_migrate import apply_audit_columns
                            apply_audit_columns()
                            
                            await run_audit(sample_size=3)
                            check_category_drift()
                            log_event(ops_log, "Auditoria e Drift Check concluídos.")
                        except Exception as audit_e:
                            log_event(ops_log, f"Falha na auditoria: {str(audit_e)[:40]}")
                        
                        audit_done_this_rest = True
                    
                    # Mantém o War Room em modo de hibernação
                    WarRoomUI.render("😴 HIBERNANDO (DESCANSO PRODUTIVO)", supabase_status, "IA OK", cycle_count, ops_log)
                    time.sleep(60)
            except Exception as e:
                log_event(ops_log, f"Erro IA/Audit: {e}")
                time.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        print("\nServidor finalizado.")
