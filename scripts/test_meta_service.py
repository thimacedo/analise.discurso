import asyncio
import json
from unittest.mock import AsyncMock, patch
from core.meta_ad_service import meta_ad_service

async def test_meta_service():
    print("🧪 [Test] Iniciando teste do MetaAdService...")
    
    # 1. Teste sem token
    meta_ad_service.access_token = None
    results = await meta_ad_service.search_ads("Candidato Teste")
    assert results == []
    print("✅ [Test] Fallback sem token OK.")

    # 2. Teste de Normalização (Lógica de Negócio)
    print("🧪 [Test] Validando normalização de dados...")
    mock_raw_ad = {
        "id": "123456789",
        "funding_entity": "Partido do Teste",
        "spend": {"lower_bound": "100", "upper_bound": "499"},
        "impressions": {"lower_bound": "1000", "upper_bound": "4999"},
        "ad_creative_bodies": ["Votem em mim!", "Teste de anúncio"],
        "page_name": "Candidato X",
        "ad_delivery_start_time": "2026-05-01",
        "ad_delivery_stop_time": None
    }
    
    normalized = meta_ad_service._normalize_ad(mock_raw_ad, "candidato_x")
    
    assert normalized['ad_id'] == "123456789"
    assert normalized['valor_min'] == 100.0
    assert normalized['valor_max'] == 499.0
    assert normalized['alcance_min'] == 1000
    assert normalized['status'] == "active"
    assert normalized['pagador'] == "Partido do Teste"
    
    print("✅ [Test] Normalização validada com sucesso!")
    print(json.dumps(normalized, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(test_meta_service())
