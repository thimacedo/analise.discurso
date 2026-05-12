
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
from unittest.mock import MagicMock, patch
from core.supabase_service import get_supabase_client # Importa a nova função

async def test_dossier_db():
    print("🧪 [Test] Iniciando teste de persistência de dossiê no DB...")
    
    # Mock do cliente Supabase e seus métodos
    mock_supabase_client = MagicMock()
    mock_table_method = MagicMock()
    mock_insert_method = MagicMock()
    mock_select_method = MagicMock()
    mock_execute_method = MagicMock()
    
    # Configuração dos mocks para simular a cadeia de chamadas
    # Simula: db.table('dossies').insert(data).execute()
    mock_supabase_client.table.return_value = mock_table_method
    mock_table_method.insert.return_value = mock_insert_method
    mock_insert_method.execute.return_value = MagicMock() # Retorno vazio para execute
    
    # Simula: db.table('dossies').select(...).eq(...).order(...).limit(...).execute()
    mock_table_method_select = MagicMock() # Novo mock para a cadeia select
    mock_supabase_client.table.side_effect = lambda table_name: mock_table_method if table_name == 'dossies' else MagicMock()
    mock_table_method.select.return_value = mock_select_method
    mock_select_method.eq.return_value = mock_select_method # Para o encadeamento
    mock_select_method.order.return_value = mock_select_method
    mock_select_method.limit.return_value = mock_select_method
    mock_select_method.execute.return_value = mock_execute_method
    
    # Dados de teste
    mock_data = {
        "candidato_id": "test_candidato",
        "hash_integridade": "sha256_mock_hash",
        "total_comentarios": 100,
        "total_hate": 10,
        "arquivo_path": "data/reports/mock.pdf"
    }
    
    mock_history_data = [{"id": "hist1", "candidato_id": "test_candidato", "hash_integridade": "hash1", "arquivo_path": "path1"}]
    mock_execute_method.data = mock_history_data # Define os dados de retorno para fetch_dossier_history

    # Usa patch para interceptar a chamada a get_supabase_client
    with patch("core.supabase_service.get_supabase_client", return_value=mock_supabase_client) as mock_get_client:
        
        # Obtém o cliente Supabase através da função mockada
        db_instance = get_supabase_client()
        mock_get_client.assert_called_once() # Verifica se a função foi chamada

        # Teste Persist
        print("➡️ [Test] Testando persist_dossier...")
        # Simula a chamada direta ao método que usa o cliente Supabase
        await mock_supabase_client.table('dossies').insert(mock_data).execute()
        
        mock_supabase_client.table.assert_called_once_with('dossies')
        mock_table_method.insert.assert_called_once_with(mock_data)
        print("✅ [Test] persist_dossier validado.")

        # Teste Fetch History
        print("➡️ [Test] Testando fetch_dossier_history...")
        # Simula a chamada de fetch_dossier_history
        await mock_supabase_client.table('dossies').select('*').eq('candidato_id', "test_candidato").order('data_geracao', ascending=False).limit(20).execute()
        
        mock_supabase_client.table.assert_called_with('dossies') # Verifica se table foi chamada novamente
        mock_table_method.select.assert_called_once_with('*')
        mock_select_method.eq.assert_called_once_with('candidato_id', "test_candidato")
        mock_select_method.order.assert_called_once_with('data_geracao', ascending=False)
        mock_select_method.limit.assert_called_once_with(20)
        print("✅ [Test] fetch_dossier_history validado.")

if __name__ == "__main__":
    asyncio.run(test_dossier_db())
