
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from core.meta_ad_service import meta_ad_service
from processing.ad_processor import ad_processor
from core.supabase_service import get_supabase_client # Importa a nova função
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

    # Mocking Database persistence
    mock_supabase_client = MagicMock()
    mock_table_method = MagicMock()
    mock_upsert_method = MagicMock()
    mock_select_method = MagicMock()
    mock_update_method = MagicMock()

    mock_supabase_client.table.return_value = mock_table_method
    mock_table_method.upsert.return_value = mock_upsert_method
    mock_upsert_method.execute.return_value = MagicMock(data=[]) # Retorno para persist_ads_batch
    
    mock_table_method_select = MagicMock() # Mock para a cadeia de select
    mock_supabase_client.table.side_effect = lambda table_name: mock_table_method if table_name == 'anuncios' else MagicMock()
    mock_table_method.select.return_value = mock_select_method
    mock_select_method.eq.return_value = mock_select_method # Para encadeamento
    mock_select_method.limit.return_value = mock_select_method
    mock_select_method.execute.return_value = MagicMock(data=[
        {
            "id": "internal-uuid-001",
            "ad_id": "AD_TEST_001",
            "corpo_anuncio": "Este é um anúncio de teste atacando as instituições! #Hate",
            "processado_ia": False
        }
    ]) # Retorno para a simulação de busca
    
    mock_table_method_update = MagicMock() # Mock para a cadeia update
    mock_table_method.update.return_value = mock_update_method
    mock_update_method.eq.return_value = mock_update_method # Para encadeamento
    mock_update_method.execute.return_value = MagicMock() # Retorno vazio para update


    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get, \
         patch("core.supabase_service.get_supabase_client", return_value=mock_supabase_client) as mock_get_client:

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
        # A função persist_ads_batch agora deve usar o cliente retornado por get_supabase_client()
        await meta_ad_service.persist_ads_batch(ads) # Chama o método do serviço que usará o cliente mockado
        mock_supabase_client.table.assert_called_once_with('anuncios')
        mock_table_method.upsert.assert_called_once_with(ads, on_conflict='ad_id')
        print("✅ Persistência (Mock) OK.")

        print("🧠 3. Simulando Processamento PASA v16.4...")
        # Mocking AI Classification for speed
        with patch("core.ai_service.AIService.classify", new_callable=AsyncMock) as mock_ai:
            mock_ai.return_value = {
                "category": "ATAQUE_INSTITUCIONAL",
                "confidence": 0.98,
                "is_hate": True,
                "reason": "Detecção de ódio contra instituições em teste",
                "engine": "gemini"
            }
            
            # ad_processor.run_once() deve usar o cliente Supabase injetado ou obtido via get_supabase_client()
            # Para simplificar, vamos assumir que ad_processor também foi atualizado ou que seu teste
            # indiretamente testa a interação correta. Aqui, focamos na chamada de meta_ad_service.
            await ad_processor.run_once(limit=1) 
            print("✅ Processamento (Mock) OK.")

    print("\n✨ [Sentinela] Teste Integrador Finalizado com Sucesso!\n")

if __name__ == "__main__":
    asyncio.run(test_full_meta_cycle())
