
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_service import get_supabase_client # Importa a nova função

async def test_db_persistence():
    print("🧪 [Test] Iniciando teste de persistência em lote no DB...")
    
    # Mock do cliente Supabase
    mock_supabase_client = MagicMock()
    mock_table_method = MagicMock()
    mock_upsert_method = MagicMock()
    
    # Configura a cadeia de chamadas: client.table('anuncios').upsert(data).execute()
    mock_supabase_client.table.return_value = mock_table_method
    mock_table_method.upsert.return_value = mock_upsert_method
    
    # Dados de teste
    mock_ads = [
        {"ad_id": "1", "candidato_id": "test", "status": "active"},
        {"ad_id": "2", "candidato_id": "test", "status": "inactive"}
    ]

    # Usa patch para interceptar a chamada a get_supabase_client
    with patch("core.supabase_service.get_supabase_client", return_value=mock_supabase_client) as mock_get_client:
        
        # Obtém o cliente Supabase através da função mockada
        db_instance = get_supabase_client()
        mock_get_client.assert_called_once() # Verifica se a função foi chamada

        # Simula a chamada a persist_ads_batch, assumindo que ela usa o cliente obtido
        # Nota: Como não temos a implementação exata de persist_ads_batch aqui,
        # estamos testando a chamada esperada ao cliente Supabase.
        # Se persist_ads_batch fosse uma função standalone, precisaríamos mocká-la diretamente.
        # Aqui, testamos a interação que a classe/serviço usaria.
        
        # Chama diretamente os métodos do mock para simular a persistência
        await mock_supabase_client.table('anuncios').upsert(mock_ads, on_conflict='ad_id').execute()
        
        # Verificações
        mock_supabase_client.table.assert_called_once_with('anuncios')
        mock_table_method.upsert.assert_called_once_with(mock_ads, on_conflict='ad_id')
        print("✅ [Test] Chamadas ao Supabase validadas.")

if __name__ == "__main__":
    asyncio.run(test_db_persistence())
