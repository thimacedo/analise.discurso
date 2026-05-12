
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
from unittest.mock import MagicMock, patch
from core.db import DatabaseClient

async def test_dossier_db():
    print("🧪 [Test] Iniciando teste de persistência de dossiê no DB...")
    
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_select = MagicMock()
    
    mock_supabase.table.return_value = mock_table
    mock_table.insert.return_value = mock_insert
    mock_table.select.return_value = mock_select
    
    mock_data = {
        "candidato_id": "test_candidato",
        "hash_integridade": "sha256_mock_hash",
        "total_comentarios": 100,
        "total_hate": 10,
        "arquivo_path": "data/reports/mock.pdf"
    }

    with patch("core.db.create_client", return_value=mock_supabase):
        db = DatabaseClient()
        db.client = mock_supabase
        
        # Teste Persist
        await db.persist_dossier(mock_data)
        mock_supabase.table.assert_called_with('dossies')
        mock_table.insert.assert_called_with(mock_data)
        print("✅ [Test] persist_dossier validado.")

        # Teste Fetch History
        mock_select.eq.return_value = mock_select
        mock_select.order.return_value = mock_select
        mock_select.limit.return_value = mock_select
        
        await db.fetch_dossier_history("test_candidato")
        mock_table.select.assert_called_with('*')
        mock_select.eq.assert_called_with('candidato_id', "test_candidato")
        print("✅ [Test] fetch_dossier_history validado.")

if __name__ == "__main__":
    asyncio.run(test_dossier_db())
