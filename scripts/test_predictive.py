
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock
from core.predictive_service import predictive_service
from core.supabase_service import get_supabase_client # Importa a nova função

async def test_predictive_engine():
    print("\n🛡️ [Sentinela] Testando Motor Preditivo (STN-008)...")
    
    # 1. Mock de Dados Temporais (Tendência de Alta)
    # Criamos uma série que sobe: 1, 2, 3, 4, 5, 10 (anomalia no final)
    mock_data = []
    for i in range(1, 6):
        mock_data.append({"data_coleta": f"2026-05-01T{i:02d}:00:00Z"})
    for i in range(10): # Pico na última hora
        mock_data.append({"data_coleta": "2026-05-01T06:00:00Z"})

    # Configura o mock do Supabase client
    mock_supabase_client = MagicMock()
    mock_query_method = MagicMock()
    mock_execute_method = MagicMock()
    
    # Configura a cadeia de chamadas: db.table().select().eq().gte().execute()
    mock_supabase_client.table.return_value = mock_query_method
    mock_query_method.select.return_value = mock_query_method
    mock_query_method.eq.return_value = mock_query_method
    mock_query_method.gte.return_value = mock_query_method
    mock_query_method.execute.return_value = mock_execute_method
    mock_execute_method.data = mock_data # Define os dados de retorno

    # Mock para a criação de alerta ativo
    mock_create_alert = AsyncMock()

    # Usa patch para interceptar a chamada a get_supabase_client e a criação de alerta
    with patch("core.supabase_service.get_supabase_client", return_value=mock_supabase_client) as mock_get_client, \
         patch.object(mock_supabase_client, 'create_active_alert', new_callable=AsyncMock) as mock_create_alert_patch:

        print("🔍 Analisando série temporal simulada (PICO detectado)...")
        # Chama o serviço que usará o cliente Supabase mockado
        result = await predictive_service.analyze_trends(days=1)
        
        mock_get_client.assert_called_once() # Verifica se get_supabase_client foi chamado
        
        # Verifica se as chamadas ao Supabase foram feitas corretamente
        mock_supabase_client.table.assert_called_once()
        mock_query_method.select.assert_called_once()
        mock_query_method.eq.assert_called_once()
        mock_query_method.gte.assert_called_once()
        mock_query_method.execute.assert_called_once()

        print(f"📊 Resultado: {json.dumps(result, indent=2)}")
        
        assert result['trend'] == "rising"
        assert result['is_anomaly'] is True
        mock_create_alert_patch.assert_called_once() # Verifica se o alerta foi criado
        print("✅ Detecção de Anomalia e Tendência de Alta: OK")

        # 2. Mock de Dados Estáveis
        mock_data_stable = []
        for i in range(1, 20): # Aumentado para 19 itens
            mock_data_stable.append({"data_coleta": f"2026-05-01T{i:02d}:00:00Z"})
        
        # Configura o mock para retornar dados estáveis
        mock_execute_method.data = mock_data_stable
        mock_get_client.reset_mock() # Reseta para verificar chamadas novamente
        mock_create_alert_patch.reset_mock() # Reseta mock de alerta

        print("\n🔍 Analisando série estável...")
        result_stable = await predictive_service.analyze_trends(days=1)
        
        mock_get_client.assert_called_once() # Verifica se get_supabase_client foi chamado novamente
        # Verifica se as chamadas ao Supabase foram feitas corretamente para dados estáveis
        mock_supabase_client.table.assert_called_once() # Should be called again for stable data query
        mock_query_method.select.assert_called_once()
        mock_query_method.eq.assert_called_once()
        mock_query_method.gte.assert_called_once()
        mock_query_method.execute.assert_called_once()
        
        assert result_stable['trend'] == "stable"
        assert result_stable['is_anomaly'] is False
        mock_create_alert_patch.assert_not_called() # Verifica se o alerta NÃO foi criado
        print("✅ Estabilidade detectada: OK")

    print("\n✨ [Sentinela] Motor Preditivo validado com sucesso!")

if __name__ == "__main__":
    asyncio.run(test_predictive_engine())
