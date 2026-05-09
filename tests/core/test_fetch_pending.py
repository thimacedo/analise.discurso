import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

# Assuming fetch_pending.py is in the same directory or importable
# If fetch_pending.py is in the root and tests are in tests/core, adjust import path
# For simplicity, assuming it's importable as 'fetch_pending'
from fetch_pending import fetch_and_process_pending
from core.supabase_service import SupabaseService # Import the actual service for mocking

# Mock settings and supabase_client_instance for tests
@pytest.fixture
def mock_settings():
    mock_settings = MagicMock()
    mock_settings.SUPABASE_URL = "http://mock-url.com"
    mock_settings.SUPABASE_KEY = "mock-key"
    return mock_settings

@pytest.fixture(autouse=True)
def patch_globals(mock_settings):
    # Patch settings and the global supabase_client_instance
    with patch('fetch_pending.settings', mock_settings):
        with patch('fetch_pending.supabase_client_instance', new_callable=AsyncMock) as mock_supabase_client:
            # Mock the methods used by fetch_and_process_pending
            mock_supabase_client.fetch_unprocessed_comments = AsyncMock()
            mock_supabase_service_instance = MagicMock(spec=SupabaseService)
            mock_supabase_service_instance.fetch_unprocessed_comments.return_value = [] # Default to empty list
            mock_supabase_service_instance.update_comment_classification = AsyncMock()
            
            # Set the return value for the globally accessed instance
            mock_supabase_client.return_value = mock_supabase_service_instance
            
            yield mock_supabase_client, mock_supabase_service_instance

# --- Test Cases for fetch_and_process_pending ---

@pytest.mark.asyncio
async def test_fetch_and_process_pending_no_comments(mock_globals):
    mock_supabase_client, mock_supabase_service = mock_globals
    mock_supabase_service.fetch_unprocessed_comments.return_value = []
    
    # Capture print output
    with patch('builtins.print') as mock_print:
        await fetch_and_process_pending()
        mock_print.assert_any_call("Nenhum comentário pendente de análise encontrado.")

@pytest.mark.asyncio
async def test_fetch_and_process_pending_with_comments(mock_globals):
    mock_supabase_client, mock_supabase_service = mock_globals
    
    mock_comments = [
        {"id": 1, "texto_limpo": "clean comment", "texto_bruto": "raw comment", "processado_ia": False},
        {"id": 2, "texto_limpo": None, "texto_bruto": "another raw comment", "processado_ia": False},
        {"id": 3, "texto_limpo": "", "texto_bruto": "empty clean comment", "processado_ia": False},
        {"id": 4, "texto_limpo": "valid comment", "texto_bruto": None, "processado_ia": False},
    ]
    mock_supabase_service.fetch_unprocessed_comments.return_value = mock_comments
    mock_supabase_service.update_comment_classification.return_value = None # Mocking the update call

    # Capture print output
    with patch('builtins.print') as mock_print:
        await fetch_and_process_pending()

    # Assertions for print output
    mock_print.assert_any_call("Encontrados 4 registros pendentes. Iniciando processamento...")
    mock_print.assert_any_call("✅ [SupabaseService] Comentário 1 atualizado.")
    mock_print.assert_any_call("✅ [SupabaseService] Comentário 2 atualizado.")
    mock_print.assert_any_call("✅ [SupabaseService] Comentário 3 atualizado.")
    mock_print.assert_any_call("✅ [SupabaseService] Comentário 4 atualizado.")
    mock_print.assert_any_call("--- Resumo do Processamento ---")
    mock_print.assert_any_call("Lote total analisado: 4 comentários")
    mock_print.assert_any_call("Atualizados com sucesso: 4")
    mock_print.assert_any_call("Ignorados (sem texto): 0")
    mock_print.assert_any_call("Falhas na atualização: 0")
    mock_print.assert_any_call("-------------------------------")

    # Assertions for calls made to the service
    assert mock_supabase_service.fetch_unprocessed_comments.call_count == 1
    assert mock_supabase_service.update_comment_classification.call_count == 4

@pytest.mark.asyncio
async def test_fetch_and_process_pending_with_empty_text(mock_globals):
    mock_supabase_client, mock_supabase_service = mock_globals
    
    mock_comments = [
        {"id": 1, "texto_limpo": None, "texto_bruto": None},
        {"id": 2, "texto_limpo": "", "texto_bruto": ""},
        {"id": 3, "texto_limpo": "  ", "texto_bruto": "  "}, # Whitespace only
    ]
    mock_supabase_service.fetch_unprocessed_comments.return_value = mock_comments

    with patch('builtins.print') as mock_print:
        await fetch_and_process_pending()

    mock_print.assert_any_call("Nenhum comentário pendente de análise encontrado.") # Should not be called if comments exist
    mock_print.assert_any_call("Ignorados (sem texto): 3")
    assert mock_supabase_service.update_comment_classification.call_count == 0 # Should not call update if text is empty

@pytest.mark.asyncio
async def test_fetch_and_process_pending_db_error_on_update(mock_globals):
    mock_supabase_client, mock_supabase_service = mock_globals
    
    mock_comments = [
        {"id": 1, "texto_limpo": "valid comment", "texto_bruto": "raw"},
        {"id": 2, "texto_limpo": "another valid", "texto_bruto": "raw2"},
    ]
    mock_supabase_service.fetch_unprocessed_comments.return_value = mock_comments
    mock_supabase_service.update_comment_classification.side_effect = Exception("Database update error")

    with patch('builtins.print') as mock_print:
        await fetch_and_process_pending()

    mock_print.assert_any_call("❌ Erro ao atualizar ID 1 no Supabase: Database update error")
    mock_print.assert_any_call("❌ Erro ao atualizar ID 2 no Supabase: Database update error")
    mock_print.assert_any_call("Falhas na atualização: 2")
    assert mock_supabase_service.update_comment_classification.call_count == 2

@pytest.mark.asyncio
async def test_fetch_and_process_pending_missing_id(mock_globals):
    mock_supabase_client, mock_supabase_service = mock_globals
    
    mock_comments = [
        {"texto_limpo": "comment without id", "texto_bruto": "raw"}, # Missing 'id'
        {"id": 2, "texto_limpo": "valid comment", "texto_bruto": "raw2"},
    ]
    mock_supabase_service.fetch_unprocessed_comments.return_value = mock_comments
    mock_supabase_service.update_comment_classification.return_value = None

    with patch('builtins.print') as mock_print:
        await fetch_and_process_pending()

    mock_print.assert_any_call("⚠️ Aviso: Registro sem ID encontrado, ignorando: {'texto_limpo': 'comment without id', 'texto_bruto': 'raw'}")
    mock_print.assert_any_call("Atualizados com sucesso: 1")
    mock_print.assert_any_call("Falhas na atualização: 1") # The one without ID counts as a failure in update count logic
    assert mock_supabase_service.update_comment_classification.call_count == 1 # Only the valid one should be updated

@pytest.mark.asyncio
async def test_fetch_and_process_pending_supabase_client_not_initialized(mock_globals):
    mock_supabase_client, mock_supabase_service = mock_globals
    
    # Simulate supabase_client_instance being None
    mock_supabase_client.return_value = None # This mock setup might be tricky, need to ensure the instance itself is None

    # Re-patch the return value of the global instance for this specific test
    with patch('fetch_pending.supabase_client_instance', None) as mock_none_client:
        with patch('builtins.print') as mock_print:
            await fetch_and_process_pending()
            mock_print.assert_any_call("❌ Erro: Cliente Supabase não inicializado. Não é possível prosseguir.")

    # Ensure no Supabase calls were made
    mock_supabase_service.fetch_unprocessed_comments.assert_not_called()
    mock_supabase_service.update_comment_classification.assert_not_called()
