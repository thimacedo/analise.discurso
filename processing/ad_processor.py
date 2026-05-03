import asyncio
import logging
from typing import List, Dict, Any
from core.db import db_client
from core.ai_service import AIService

logger = logging.getLogger("AdProcessor")

class AdProcessor:
    """
    Processador de inteligência para anúncios da Meta.
    Aplica o Protocolo PASA v16.4 para classificar o conteúdo.
    """
    
    def __init__(self):
        self.ai_service = AIService()

    async def process_pending_ads(self, limit: int = 50):
        """Busca anúncios não processados e aplica classificação de IA."""
        ads = await db_client.fetch_unprocessed_ads(limit=limit)
        
        if not ads:
            logger.info("ℹ️ [AdProcessor] Nenhum anúncio pendente de processamento.")
            return

        logger.info(f"⛏️ [AdProcessor] Processando {len(ads)} anúncios pendentes...")
        
        for ad in ads:
            ad_id = ad['id']
            corpo = ad.get('corpo_anuncio') or ""
            
            if not corpo:
                # Se não tem corpo, marca como processado neutro
                await db_client.update_ad_classification(ad_id, {
                    "processado_ia": True,
                    "categoria_ia": "NEUTRO",
                    "is_hate": False
                })
                continue

            try:
                # Classifica via PASA v16.4
                classification = await self.ai_service.classify(corpo)
                
                update_data = {
                    "categoria_ia": classification['category'],
                    "confianza_ia": classification['confidence'],
                    "is_hate": classification['is_hate'],
                    "processado_ia": True
                }
                
                await db_client.update_ad_classification(ad_id, update_data)
                logger.info(f"   ✅ Anúncio {ad['ad_id']} classificado como {classification['category']}.")
                
            except Exception as e:
                logger.error(f"   ⚠️ Erro ao processar anúncio {ad['ad_id']}: {e}")

ad_processor = AdProcessor()
