"""
PASA v42.1 - Mass Classify Script: Motor de Classificação Massiva MCF v2.0
"""
import asyncio
import sys
import os
import logging
from datetime import datetime

# Ajuste de path para encontrar core
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

try:
    from core.ai_service import ai_service
    from core.config import settings
except ImportError:
    print("Erro ao importar core.ai_service. Verifique se o PYTHONPATH está correto.")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - CLASSIFY - %(message)s')
logger = logging.getLogger("MassClassify")

async def process_mass_classification(limit: int = 50):
    """
    Executa a classificação em lote usando o protocolo MCF v2.0 e CCF Framework.
    """
    logger.info(f"Iniciando lote de classificação (limite: {limit})...")
    try:
        processed_count = await ai_service.run_batch_classification(limit=limit)
        if processed_count > 0:
            logger.info(f"Sucesso: {processed_count} comentários processados e persistidos.")
        else:
            logger.info("Nenhum comentário pendente para classificação.")
        return processed_count
    except Exception as e:
        logger.error(f"Falha na classificação em lote: {e}")
        return 0

if __name__ == "__main__":
    # Permite rodar como script independente
    print(f"--- [PASA v42.1] Mass Classify Engine (Provider: {settings.IA_PROVIDER}) ---")
    asyncio.run(process_mass_classification())
