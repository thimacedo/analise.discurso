import logging
from processing.common import BaseWorker
from core.pasa_auditor import PasaForensicsService

logger = logging.getLogger("main-orchestrator")
pasa_service = PasaForensicsService()

class MainOrchestrator(BaseWorker):
    """
    Orquestrador central com integração PASA v16.4.
    """
    def __init__(self, name="MainOrchestrator"):
        super().__init__(name=name)

    async def process_item(self, item):
        try:
            # Integração PASA forense
            analysis = await pasa_service.audit_content(item.get('text'))
            item['pasa_score'] = analysis.get('score')
            item['is_hate'] = analysis.get('is_hate')
            
            logger.info(f"[{self.name}] Item processado com PASA. IsHate: {item['is_hate']}")
            return item
        except Exception as e:
            logger.error(f"[{self.name}] Erro na orquestração: {e}")
            raise e
