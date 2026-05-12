# run_long_scrape.py
import sys
import asyncio
import logging
import random

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from workers.scrapers.instagram_worker import InstagramWorker

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

# A LISTA DE ALVOS ESTRATÉGICOS
# Regra de Ouro: Comece com perfis de notícias/jornais (baixo risco de bloqueio) para validar a infraestrutura.
# Só coloque políticos polarizados depois que a conta sobreviver à primeira rodada.
TARGETS = [
    "oglobo_oficial",   
    "folhadesp",        
    "metropolesinstavel",
    # Adicione mais alvos políticos aqui amanhã...
]

async def main():
    logger = logging.getLogger("MaestroEndurance")
    total_alerts_saved = 0

    logger.info("🚀 INICIANDO OPERAÇÃO DE INFILTRAÇÃO LONGA (MODO STEALTH)")
    logger.info(f"🎯 Alvos na lista: {len(TARGETS)}")

    for index, target in enumerate(TARGETS):
        logger.info(f"\n{'='*50}")
        logger.info(f"📍 Iniciando extração para: @{target} ({index+1}/{len(TARGETS)})")
        
        try:
            # Instancia o worker com um limite seguro (12 posts por sessão)
            worker = InstagramWorker(target_profile=target, max_posts=12)
            dados = await worker.execute()
            
            if dados:
                total_alerts_saved += len(dados)
                logger.info(f"✅ @{target} rendeu {len(dados)} alertas classificados pelo PASA.")
            else:
                logger.warning(f"⚠️ @{target} não rendeu dados ou a sessão foi bloqueada.")

        except Exception as e:
            logger.error(f"❌ Falha crítica ao processar @{target}: {e}")

        # A REGRA DE OURO: MACRO-DELAY ENTRE PERFIS
        if index < len(TARGETS) - 1:
            # Pausa aleatória entre 120 e 300 segundos (2 a 5 minutos)
            pause_secs = random.randint(120, 300)
            logger.info(f"⏳ Perfil finalizado. Entrando em modo stealth por {pause_secs // 60} minutos e {pause_secs % 60} segundos...")
            
            # Contagem regressiva visual no terminal
            for i in range(pause_secs):
                remaining = pause_secs - i
                if remaining % 30 == 0: # Printa a cada 30 segundos para não poluir
                    sys.stdout.write(f"\r⏳ Restam: {remaining // 60}m {remaining % 60}s   ")
                    sys.stdout.flush()
                await asyncio.sleep(1)
            sys.stdout.write("\r✅ Pausa finalizada. Próximo alvo!          \n")

    logger.info(f"\n🏁 OPERAÇÃO FINALIZADA!")
    logger.info(f"📊 Total de alertas coletados e salvos no Supabase: {total_alerts_saved}")

if __name__ == "__main__":
    asyncio.run(main())
