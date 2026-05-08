import asyncio
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db import DatabaseClient

async def test_db_persistence():
    print("🧪 [Test] Iniciando teste de persistência em lote no DB...")
    
    # Mock do cliente Supabase
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_upsert = MagicMock()
    
    mock_supabase.table.return_value = mock_table
    mock_table.upsert.return_value = mock_upsert
    
    # Dados de teste
    mock_ads = [
        {"ad_id": "1", "candidato_id": "test", "status": "active"},
        {"ad_id": "2", "candidato_id": "test", "status": "inactive"}
    ]

    with patch("core.db.create_client", return_value=mock_supabase):
        db = DatabaseClient()
        # Injeta o mock explicitamente se necessário, mas o create_client deve resolver
        db.client = mock_supabase
        
        await db.persist_ads_batch(mock_ads)
        
        # Verificações
        mock_supabase.table.assert_called_with('anuncios')
        mock_table.upsert.assert_called_with(mock_ads, on_conflict='ad_id')
        print("✅ [Test] Chamadas ao Supabase validadas.")

if __name__ == "__main__":
    asyncio.run(test_db_persistence())
