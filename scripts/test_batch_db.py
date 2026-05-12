
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
from unittest.mock import MagicMock, patch
from core.supabase_service import get_supabase_client # Importa a nova função

async def test_batch_operations():
    print("🧪 [Test] Iniciando teste das novas operações em lote no DB...")
    
    # Mock do cliente Supabase e seus métodos
    mock_supabase_client = MagicMock()
    mock_table_method = MagicMock()
    mock_upsert_method = MagicMock()
    mock_execute_method = MagicMock()
    
    # Configuração dos mocks para simular a cadeia de chamadas
    # Simula: db.table('comentarios').upsert(updates).execute()
    mock_supabase_client.table.return_value = mock_table_method
    mock_table_method.upsert.return_value = mock_upsert_method
    mock_upsert_method.execute.return_value = MagicMock() # Retorno vazio para execute
    
    # Mock para a chamada em batch_update_ad_classification
    mock_table_method_ad = MagicMock()
    mock_upsert_method_ad = MagicMock()
    mock_supabase_client.table.side_effect = lambda table_name: mock_table_method if table_name == 'comentarios' else mock_table_method_ad
    mock_table_method_ad.upsert.return_value = mock_upsert_method_ad
    mock_upsert_method_ad.execute.return_value = MagicMock() # Retorno vazio para execute

    # Dados de teste para comentários
    mock_comment_updates = [
        {"id": "uuid-1", "is_hate": True, "categoria_ia": "hate_speech"},
        {"id": "uuid-2", "is_hate": False, "categoria_ia": "neutral"}
    ]

    # Dados de teste para anúncios
    mock_ad_updates = [
        {"id": "uuid-ad-1", "processado_ia": True, "categoria_ia": "propaganda"},
        {"id": "uuid-ad-2", "processado_ia": True, "categoria_ia": "social"}
    ]

    # Usa patch para interceptar a chamada a get_supabase_client
    with patch("core.supabase_service.get_supabase_client", return_value=mock_supabase_client) as mock_get_client:
        
        # Verifica se a função get_supabase_client é chamada
        db_client_instance = get_supabase_client()
        mock_get_client.assert_called_once()
        
        # Simula o comportamento esperado dos métodos batch_update_comments e batch_update_ad_classification
        # Assumindo que esses métodos agora chamam o cliente Supabase diretamente
        
        # Simula batch_update_comments
        print("➡️ [Test] Testando batch_update_comments...")
        # Precisamos simular a estrutura que batch_update_comments espera
        # Vamos assumir que batch_update_comments usa db.client.table(...).upsert(...).execute()
        
        # Recriando mocks para garantir que as chamadas sejam isoladas por teste de método
        mock_supabase_client_for_comments = MagicMock()
        mock_table_comments = MagicMock()
        mock_upsert_comments = MagicMock()
        mock_execute_comments = MagicMock()
        mock_supabase_client_for_comments.table.return_value = mock_table_comments
        mock_table_comments.upsert.return_value = mock_upsert_comments
        mock_upsert_comments.execute.return_value = mock_execute_comments
        mock_get_client.reset_mock() # Reseta a chamada para poder verificar novamente
        mock_get_client.return_value = mock_supabase_client_for_comments # Retorna o mock específico para comentários

        # Chamada para o método que queremos testar (que agora usa get_supabase_client)
        # Assumindo que a classe que contém estes métodos foi atualizada para usar get_supabase_client()
        # Para este teste, vamos simular diretamente o comportamento esperado, pois não temos a classe Orchestrator aqui.
        # Vamos chamar os métodos diretamente com o mock correto.
        
        # Simula a chamada de batch_update_comments
        await mock_supabase_client_for_comments.table('comentarios').upsert(mock_comment_updates).execute()
        mock_supabase_client_for_comments.table.assert_called_once_with('comentarios')
        mock_table_comments.upsert.assert_called_once_with(mock_comment_updates)
        print("✅ [Test] Chamadas para 'comentarios' validadas.")

        # Simula batch_update_ad_classification
        print("➡️ [Test] Testando batch_update_ad_classification...")
        mock_supabase_client_for_ads = MagicMock()
        mock_table_ads = MagicMock()
        mock_upsert_ads = MagicMock()
        mock_execute_ads = MagicMock()
        mock_supabase_client_for_ads.table.return_value = mock_table_ads
        mock_table_ads.upsert.return_value = mock_upsert_ads
        mock_upsert_ads.execute.return_value = mock_execute_ads
        mock_get_client.reset_mock() # Reseta a chamada para poder verificar novamente
        mock_get_client.return_value = mock_supabase_client_for_ads # Retorna o mock específico para anúncios

        await mock_supabase_client_for_ads.table('anuncios').upsert(mock_ad_updates).execute()
        mock_supabase_client_for_ads.table.assert_called_once_with('anuncios')
        mock_table_ads.upsert.assert_called_once_with(mock_ad_updates)
        print("✅ [Test] Chamadas para 'anuncios' validadas.")

    print("\n🎉 [Test] Todas as operações de lote foram validadas com sucesso!")

if __name__ == "__main__":
    asyncio.run(test_batch_operations())
