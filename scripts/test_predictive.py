import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from core.predictive_service import predictive_service
from core.db import db_client

async def test_predictive_engine():
    print("\n🛡️ [Sentinela] Testando Motor Preditivo (STN-008)...")
    
    # 1. Mock de Dados Temporais (Tendência de Alta)
    # Criamos uma série que sobe: 1, 2, 3, 4, 5, 10 (anomalia no final)
    mock_data = []
    for i in range(1, 6):
        mock_data.append({"data_coleta": f"2026-05-01T{i:02d}:00:00Z"})
    for i in range(10): # Pico na última hora
        mock_data.append({"data_coleta": "2026-05-01T06:00:00Z"})

    # Configura o mock do Supabase
    db_client.client = MagicMock()
    mock_query = db_client.client.table().select().eq().gte().execute = MagicMock(
        return_value=MagicMock(data=mock_data)
    )
    db_client.create_active_alert = AsyncMock()

    print("🔍 Analisando série temporal simulada (PICO detectado)...")
    result = await predictive_service.analyze_trends(days=1)
    
    print(f"📊 Resultado: {json.dumps(result, indent=2)}")
    
    assert result['trend'] == "rising"
    assert result['is_anomaly'] is True
    assert db_client.create_active_alert.called
    print("✅ Detecção de Anomalia e Tendência de Alta: OK")

    # 2. Mock de Dados Estáveis
    mock_data_stable = []
    for i in range(1, 20): # Aumentado para 19 itens
        mock_data_stable.append({"data_coleta": f"2026-05-01T{i:02d}:00:00Z"})
    
    mock_query.return_value = MagicMock(data=mock_data_stable)
    db_client.create_active_alert.reset_mock()

    print("\n🔍 Analisando série estável...")
    result_stable = await predictive_service.analyze_trends(days=1)
    assert result_stable['trend'] == "stable"
    assert result_stable['is_anomaly'] is False
    assert not db_client.create_active_alert.called
    print("✅ Estabilidade detectada: OK")

    print("\n✨ [Sentinela] Motor Preditivo validado com sucesso!")

if __name__ == "__main__":
    asyncio.run(test_predictive_engine())
