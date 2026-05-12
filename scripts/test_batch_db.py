
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
from unittest.mock import MagicMock, patch
from core.db import DatabaseClient

async def test_batch_operations():
    print("🧪 [Test] Iniciando teste das novas operações em lote no DB...")
    
    # Mock do cliente Supabase
    mock_supabase = MagicMock()
    mock_table = MagicMock()
    mock_execute = MagicMock()
    
    mock_supabase.table.return_value = mock_table
    mock_table.upsert.return_value = mock_table # Encadeamento
    mock_table.execute.return_value = mock_execute
    
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

    with patch("core.db.create_client", return_value=mock_supabase):
        db = DatabaseClient()
        db.client = mock_supabase
        
        print("➡️ [Test] Testando batch_update_comments...")
        await db.batch_update_comments(mock_comment_updates)
        
        # Verificações Comentários
        mock_supabase.table.assert_any_call('comentarios')
        mock_table.upsert.assert_any_call(mock_comment_updates)
        print("✅ [Test] Chamadas para 'comentarios' validadas.")

        print("➡️ [Test] Testando batch_update_ad_classification...")
        await db.batch_update_ad_classification(mock_ad_updates)
        
        # Verificações Anúncios
        mock_supabase.table.assert_any_call('anuncios')
        mock_table.upsert.assert_any_call(mock_ad_updates)
        print("✅ [Test] Chamadas para 'anuncios' validadas.")

    print("\n🎉 [Test] Todas as operações de lote foram validadas com sucesso!")

if __name__ == "__main__":
    asyncio.run(test_batch_operations())
