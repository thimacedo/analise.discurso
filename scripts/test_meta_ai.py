import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from processing.ad_processor import AdProcessor

async def test_meta_ai_integration():
    print("🧪 [Test] Iniciando teste de classificação de anúncios Meta...")
    
    # Mock de anúncio pendente
    mock_ads = [
        {
            "id": "ad_uuid_1",
            "ad_id": "meta_123",
            "corpo_anuncio": "Esses políticos são todos uns ratos e deveriam estar presos!",
            "processado_ia": False
        }
    ]

    # Mock da classificação PASA
    mock_classification = {
        "category": "INSULTO_AD_HOMINEM",
        "confidence": 0.98,
        "is_hate": True,
        "reason": "Uso de termo desumanizante 'ratos'."
    }

    with patch("core.db.db_client.fetch_unprocessed_ads", new_callable=AsyncMock) as mock_fetch, \
         patch("core.db.db_client.update_ad_classification", new_callable=AsyncMock) as mock_update, \
         patch("core.ai_service.AIService.classify", new_callable=AsyncMock) as mock_classify:
        
        mock_fetch.return_value = mock_ads
        mock_classify.return_value = mock_classification
        
        processor = AdProcessor()
        await processor.process_pending_ads(limit=1)
        
        # Verificações
        mock_fetch.assert_called_once()
        mock_classify.assert_called_with(mock_ads[0]['corpo_anuncio'])
        
        # Verifica se o update foi chamado com os dados corretos
        expected_update = {
            "categoria_ia": "INSULTO_AD_HOMINEM",
            "confianza_ia": 0.98,
            "is_hate": True,
            "processado_ia": True
        }
        mock_update.assert_called_with("ad_uuid_1", expected_update)
        
        print("✅ [Test] Fluxo de classificação PASA para anúncios validado!")

if __name__ == "__main__":
    asyncio.run(test_meta_ai_integration())
