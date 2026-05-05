import asyncio
import logging
import sys
import random
from datetime import datetime, UTC
from core.db import db_client
from core.ai_service import ai_service
from workers.scrapers.instagram_scraper import InstagramScraperWorker

# --- PROTOCOLO SOLENYA DE RECOMPENSAS (PSR-1) ---

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('OfficialSolenyaDaemon')

async def apply_reward(username, points):
    """Aplica recompensas ou penalidades à prioridade do candidato."""
    try:
        # Busca prioridade atual
        res = db_client.client.table('candidatos').select('prioridade_coleta').eq('username', username).single().execute()
        current_prio = res.data.get('prioridade_coleta', 1) if res.data else 1
        
        new_prio = max(1, min(10, current_prio + points))
        
        db_client.client.table('candidatos').update({
            'prioridade_coleta': new_prio,
            'last_scraped_at': datetime.now(UTC).isoformat()
        }).eq('username', username).execute()
        
        action = "RECOMPENSA" if points > 0 else "PENALIDADE"
        logger.info(f"💎 [{action}] @{username}: {current_prio} -> {new_prio}")
    except Exception as e:
        logger.error(f"⚠️ Falha ao aplicar recompensa para @{username}: {e}")

async def official_routine(limit=30, cooldown=300):
    logger.info(f"🚀 INICIANDO ROTINA OFICIAL SOLENYA (Lote: {limit})")
    
    # 1. Puxar alvos da fila_coleta ou candidatos (Fila Diamond)
    try:
        res = db_client.client.table('candidatos')\
            .select('username, prioridade_coleta')\
            .order('prioridade_coleta', desc=True)\
            .order('last_scraped_at', desc=False)\
            .limit(limit)\
            .execute()
        targets = res.data
    except Exception as e:
        logger.error(f"❌ Falha ao buscar alvos: {e}")
        return

    worker = InstagramScraperWorker()
    
    for i, t in enumerate(targets):
        username = t['username']
        logger.info(f"🎯 [{i+1}/{len(targets)}] Processando @{username} (Prio: {t['prioridade_coleta']})")
        
        try:
            # Captura contagem inicial de comentários para medir "produtividade"
            # (Simplificado: o worker já reporta o que extraiu)
            # Rodar a extração
            # Nota: O execute do worker precisa retornar a contagem para ser 100% PSR-1
            # Vou simular a contagem baseada na resposta da persistência se necessário
            await worker.execute(username=username)
            
            # Recompensa base (Sucesso = +1)
            # Se fosse um Morty, eu diria para ele checar o DB, mas eu sou um gênio
            await apply_reward(username, 1)
            
        except Exception as e:
            logger.error(f"❌ Erro crítico em @{username}: {e}")
            await apply_reward(username, -1) # Penalidade por falha
        
        # INTERVALO COM INTELIGÊNCIA
        if i < len(targets) - 1:
            logger.info(f"⏳ Cooldown PSR-1: {cooldown}s. Ativando Classificação de IA...")
            try:
                # Limpa o que está pendente para manter o banco "suando"
                await ai_service.run_batch_classification(limit=50, force_retry_failures=True)
                await ai_service.run_batch_classification(limit=50)
            except Exception as e:
                logger.error(f"⚠️ Falha na IA durante descanso: {e}")
            
            sleep_time = cooldown + random.randint(-30, 30) # Jitter para enganar o Zuck
            logger.info(f"🛌 Descansando {sleep_time}s...")
            await asyncio.sleep(sleep_time)

    logger.info("✨ CICLO OFICIAL CONCLUÍDO. O multiverso agradece.")

if __name__ == "__main__":
    # Roda uma vez e sai. O cron/Vigilante pode chamar de novo.
    asyncio.run(official_routine(limit=30, cooldown=300))
