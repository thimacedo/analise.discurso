import asyncio
import sys
import os
from datetime import datetime

# Adiciona o root do projeto ao sys.path de forma robusta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.orquestrador import Orchestrator
from core.config import settings

async def main():
    print(f"📊 [KPI-UPDATE] Iniciando Atualização de Métricas Diamond v{settings.VERSION}")
    orc = Orchestrator()
    
    # 1. Busca e Normaliza dados atuais do DB
    df = await orc.fetch_and_normalize()
    
    if df.empty:
        print("🛑 Erro: Nenhum dado encontrado para atualizar KPIs.")
        return

    # 2. Roda Mineração, Clustering e Persistência
    print("⛏️ Minerando tendências e atualizando métricas diárias...")
    await orc.process_and_mine(df)
    
    # 3. Análise Preditiva
    await orc.run_predictive_cycle()
    
    print(f"✅ KPIs atualizados com sucesso em {datetime.now().strftime('%H:%M:%S')}!")

if __name__ == '__main__':
    asyncio.run(main())
