# run_long_scrape.py
import sys
import asyncio
import logging
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from workers.scrapers.instagram_worker import InstagramWorker
from core.supabase_service import save_alerts, get_next_targets_to_scrape, update_last_scraped_at
from core.worker_auditor import audit_worker_result

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

async def main():
    logger = logging.getLogger("MaestroDinamico")
    total_alerts_saved = 0

    # BUSCA DINÂMICA: Pega os 5 alvos mais quentes e esquecidos do banco
    targets = get_next_targets_to_scrape(limit=5)
    
    if not targets:
        logger.warning("⚠️ Nenhum alvo ATIVO encontrado na tabela 'candidatos'.")
        return

    logger.info("🚀 INICIANDO OPERAÇÃO DINÂMICA (MODO STEALTH + AUDITORIA)")
    logger.info(f"🎯 Alvos selecionados pelo banco: {targets}")

    for index, target in enumerate(targets):
        logger.info(f"\n{'='*50}")
        logger.info(f"📍 Iniciando extração para: @{target} ({index+1}/{len(targets)})")
        
        try:
            worker = InstagramWorker(target_profile=target, max_posts=3)
            dados = await worker.execute()
            
            if dados:
                # 1. O AUDITOR AVALIA O PROCESSO
                process_is_healthy = audit_worker_result(worker.name, dados)
                
                if not process_is_healthy:
                    logger.error("🛑 PROCESSO COMPROMETIDO POR ATALHO. Operação interrompida.")
                    break 
                
                # 2. SALVA OS ALERTAS
                logger.info(f"💾 Processo íntegro. Salvando {len(dados)} alertas...")
                success = save_alerts(dados)
                if success:
                    total_alerts_saved += len(dados)
                    logger.info("✅ Sincronização concluída.")
            else:
                logger.warning(f"⚠️ @{target} não rendeu dados ou sessão bloqueada.")

        except Exception as e:
            logger.error(f"❌ Falha mecânica ao processar @{target}: {e}")

        # IMPORTANTE: Atualiza o last_scraped_at do alvo, mesmo se falhar
        # Para não ficar preso no mesmo alvo quebrado no próximo ciclo
        update_last_scraped_at(target)
        logger.info(f"⏱️ Timestamp de raspagem atualizado para @{target}.")

        # MACRO-DELAY (2 a 5 minutos)
        if index < len(targets) - 1:
            pause_secs = random.randint(120, 300)
            logger.info(f"⏳ Entrando em modo stealth por {pause_secs // 60} minutos...")
            
            for i in range(pause_secs):
                remaining = pause_secs - i
                if remaining % 30 == 0:
                    sys.stdout.write(f"\r⏳ Restam: {remaining // 60}m {remaining % 60}s   ")
                    sys.stdout.flush()
                await asyncio.sleep(1)
            sys.stdout.write("\r✅ Pausa finalizada. Próximo alvo!          \n")

    logger.info(f"\n🏁 CICLO DE COLETA CONCLUÍDO!")
    logger.info(f"📊 Total de alertas íntegros: {total_alerts_saved}")

if __name__ == "__main__":
    asyncio.run(main())
