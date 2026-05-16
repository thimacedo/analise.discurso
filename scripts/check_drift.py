"""
PASA v44 - Drift Check: Monitora a distribuição de categorias para detectar viés
"""
import logging
from core.db import db_client as db

logger = logging.getLogger("DriftCheck")

def check_category_drift():
    """
    Analisa a distribuição estatística das classificações recentes.
    """
    logger.info("Iniciando checagem de deriva (Drift Check)...")

    try:
        # Busca total processado - PASA v44.2.1: Corrigido erro de sintaxe usando select com filtro is_not_null
        # O método .not() é palavra reservada, usamos filter ou o formato correto do postgrest-py
        res_total = db.client.table('comentarios').select('id', count='exact').not_('categoria_ia', 'is', None).execute()
        total = res_total.count if res_total.count is not None else 0

        if total == 0:
            logger.info("Nenhum dado processado para análise.")
            return

        categories = ['NEUTRO', 'ODIO_IDENTITARIO', 'AMEACA', 'VIOLENCIA_GENERO', 'ATAQUE_INSTITUCIONAL', 'RIGOR_CRIMINAL', 'INSULTO_AD_HOMINEM']

        results = {}
        for cat in categories:
            res_cat = db.client.table('comentarios').select('id', count='exact').eq('categoria_ia', cat).execute()
            count = res_cat.count if res_cat.count is not None else 0
            percentage = (count / total) * 100
            results[cat] = percentage

            # Alertas de Deriva
            if cat == 'NEUTRO' and percentage < 70:
                logger.warning(f"🚨 ALERTA DE DERIVA: NEUTRO em {percentage:.1f}%. Possível super-classificação de ódio.")
            if cat == 'ODIO_IDENTITARIO' and percentage > 20:
                logger.warning(f"🚨 ALERTA DE DERIVA: ODIO_IDENTITARIO em {percentage:.1f}%. Possível viés ou ataque coordenado.")

        logger.info(f"Distribuição: {results}")

    except Exception as e:
        logger.error(f"Erro no Drift Check: {e}")

if __name__ == "__main__":
    check_category_drift()
