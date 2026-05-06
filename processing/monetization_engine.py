import logging
from typing import Dict, Any

logger = logging.getLogger("MonetizationEngine")

class MonetizationEngine:
    @staticmethod
    def extract_monetization_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrai e normaliza informações financeiras."""
        logger.info(f"Processando dados de monetização para AD: {raw_data.get('ad_id')}")
        
        return {
            "ad_id": raw_data.get('ad_id'),
            "pagador": raw_data.get('pagador', 'Desconhecido'),
            "valor_estimado": (raw_data.get('valor_min', 0) + raw_data.get('valor_max', 0)) / 2,
            "alcance_estimado": (raw_data.get('alcance_min', 0) + raw_data.get('alcance_max', 0)) / 2,
            "risco_monetizacao": "High" if raw_data.get('valor_max', 0) > 10000 else "Low"
        }
