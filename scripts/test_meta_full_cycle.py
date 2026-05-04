import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from core.meta_ad_service import meta_ad_service
from processing.ad_processor import ad_processor
from core.db import db_client
from core.config import settings

async def test_full_meta_cycle():
    print("\n🛡️ [Sentinela] Iniciando Teste Integrador: Ciclo Meta Ads...")
    
    # Mocking Meta API Response
    mock_response = {
        "data": [
            {
                "id": "AD_TEST_001",
                "ad_creation_time": "2026-05-01T12:00:00Z",
                "ad_delivery_start_time": "2026-05-01",
                "ad_delivery_stop_time": None,
                "ad_creative_bodies": ["Este é um anúncio de teste atacando as instituições! #Hate"],
                "page_id": "PAGE_001",
                "page_name": "Página Opositora",
                "spend": {"lower_bound": "100", "upper_bound": "499"},
                "impressions": {"lower_bound": "1000", "upper_bound": "4999"},
                "funding_entity": "Movimento Teste"
            }
        ],
        "paging": {"next": None}
    }

    # Mocking Database persistence to avoid real side effects if DB not configured
    # But for this test, let's mock the 'anuncios' table specifically
    db_client.client = MagicMock()
    mock_upsert = db_client.client.table().upsert().execute = MagicMock(return_value=MagicMock(data=[]))
    mock_select = db_client.client.table().select().eq().limit().execute = MagicMock(
        return_value=MagicMock(data=[
            {
                "id": "internal-uuid-001",
                "ad_id": "AD_TEST_001",
                "corpo_anuncio": "Este é um anúncio de teste atacando as instituições! #Hate",
                "processado_ia": False
            }
        ])
    )
    mock_update = db_client.client.table().update().eq().execute = MagicMock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json = lambda: mock_response
        mock_get.return_value.raise_for_status = lambda: None

        print("🔍 1. Simulando Busca na Meta API...")
        meta_ad_service.access_token = "fake-token" # Forçar execução
        ads = await meta_ad_service.search_ads("Candidato X")
        assert len(ads) == 1
        assert ads[0]['ad_id'] == "AD_TEST_001"
        print(f"✅ Encontrado: {ads[0]['ad_id']}")

        print("💾 2. Simulando Persistência...")
        await db_client.persist_ads_batch(ads)
        print("✅ Persistência (Mock) OK.")

        print("🧠 3. Simulando Processamento PASA v16.4...")
        # Mocking AI Classification for speed
        with patch("core.ai_service.AIService.classify", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = {
                "category": "ATAQUE_INSTITUCIONAL",
                "confidence": 0.98,
                "is_hate": True,
                "reason": "Detecção de ódio contra instituições em teste"
            }
            
            await ad_processor.process_pending_ads(limit=1)
            print("✅ Processamento (Mock) OK.")

    print("\n✨ [Sentinela] Teste Integrador Finalizado com Sucesso!\n")

if __name__ == "__main__":
    asyncio.run(test_full_meta_cycle())
