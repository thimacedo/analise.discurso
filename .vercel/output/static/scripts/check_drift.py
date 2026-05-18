"""
PASA v44.3 - Drift Check: Monitora a distribuição de categorias (Versão Robusta)
"""
import logging
from collections import Counter
from core.supabase_service import get_supabase_client

logger = logging.getLogger("DriftCheck")

def check_category_drift():
    """
    Analisa a distribuição estatística das classificações recentes de forma robusta.
    """
    logger.info("Iniciando checagem de deriva (Drift Check) v44.3...")
    db = get_supabase_client()
    
    try:
        # Query simplificada para evitar erros de encadeamento no Supabase Client
        # Buscamos os últimos 1000 registros classificados
        response = db.table('comentarios').select('categoria_ia').not_('categoria_ia', 'is', 'null').limit(1000).execute()
        
        if not response.data:
            logger.info("Sem dados classificados para análise.")
            return

        categories = [item['categoria_ia'] for item in response.data]
        total = len(categories)
        
        logger.info(f"Distribuição atual do modelo (Amostra: {total}):")
        
        # Contagem em Python para evitar complexidade no banco
        counts = Counter(categories)
        
        results = {}
        for cat, count in counts.items():
            percentage = (count / total) * 100
            results[cat] = percentage
            logger.info(f"  - {cat}: {percentage:.2f}% ({count})")
            
            # Alertas de Deriva
            if cat == 'NEUTRO' and percentage < 70:
                logger.warning(f"  🚨 ALERTA DE DERIVA: NEUTRO caiu para {percentage:.2f}%. O modelo pode estar super-classificando como ódio.")
            if cat == 'ODIO_IDENTITARIO' and percentage > 20:
                logger.warning(f"  🚨 ALERTA DE DERIVA: ODIO_IDENTITARIO acima de {percentage:.2f}%. Possível viés ou ataque coordenado.")

    except Exception as e:
        logger.error(f"Erro no Drift Check v44.3: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    check_category_drift()
