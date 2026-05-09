# tests/test_fetch_pending.py
import pytest
import asyncio
from unittest.mock import patch, MagicMock

# Importar o script a ser testado
from fetch_pending import fetch_and_process_pending

# --- Mocks ---
# Usaremos patch para substituir os módulos/objetos reais pelos mocks
# Precisaremos que o fetch_pending.py importe os mocks em vez dos reais

# Mock de configuração
@pytest.fixture(scope="module")
def mock_settings():
    # O script real importa `core.config` e usa `settings`.
    # Precisamos que ele importe nosso mock em vez do real.
    # Isso é feito com patch.object ou patch.dict antes de importar o módulo.
    # Para este fixture, vamos apenas retornar um objeto mock simples que pode ser injetado.
    class MockSettings:
        SUPABASE_URL = "http://mock-supabase.com"
        SUPABASE_KEY = "mock-key"
        IA_PROVIDER = "mock" # Necessário se fetch_pending.py usasse IA_PROVIDER
    return MockSettings()

# Mock do Supabase Service
@pytest.fixture(scope="module")
def mock_supabase_service():
    # Vamos criar um mock que o fetch_pending.py possa usar
    # Precisamos que `fetch_pending.py` importe `supabase_client_instance`
    # de um módulo que podemos controlar.
    # O script real importa de `core.supabase_service`.
    # Vamos criar um mock `MockSupabaseService` e fazer `supabase_client_instance`
    # no *nosso* módulo de teste ser essa instância mock.
    # O `fetch_pending.py` importa `supabase_client_instance` diretamente,
    # então precisamos fazer o patch em `fetch_pending.supabase_client_instance`.
    
    # Retorna uma instância mock configurável
    return MagicMock()

# --- Testes ---

# Função de ajuda para rodar corrotinas em testes pytest
def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro(*args, **kwargs))
        finally:
            loop.close()
    return wrapper

# --- Configuração dos Mocks ---
# Vamos usar um patch para substituir `core.supabase_service.supabase_client_instance`
# e `core.config.settings` quando `fetch_pending.py` for importado.

# Definindo a classe MockSupabaseService aqui para ser usada no patch
class MockSupabaseService:
    def __init__(self, *args, **kwargs):
        self.fetch_unprocessed_comments_return_value = []
        self.update_comment_classification_call_count = 0
        self.fetch_unprocessed_comments_call_count = 0
        self.fetch_unprocessed_comments_kwargs = {}
        self.update_comment_classification_kwargs_list = []
        self.raise_fetch_error = None
        self.raise_update_error = None

    async def fetch_unprocessed_comments(self, limit: int = 100, org_id: str = None) -> List[Dict[str, Any]]:
        self.fetch_unprocessed_comments_call_count += 1
        self.fetch_unprocessed_comments_kwargs = {'limit': limit, 'org_id': org_id}
        print(f"[MockSupabaseService] fetch_unprocessed_comments called with limit={limit}, org_id={org_id}")
        if self.raise_fetch_error:
            raise self.raise_fetch_error
        await asyncio.sleep(0.01)
        return self.fetch_unprocessed_comments_return_value

    async def update_comment_classification(self, comment_id: str, data: Dict[str, Any]):
        self.update_comment_classification_call_count += 1
        self.update_comment_classification_kwargs_list.append({'comment_id': comment_id, 'data': data})
        print(f"[MockSupabaseService] update_comment_classification called for {comment_id} with data: {data}")
        if self.raise_update_error:
            raise self.raise_update_error
        await asyncio.sleep(0.01)

# Usando patch.object para substituir `supabase_client_instance` no módulo `fetch_pending`
# e `settings` no módulo `fetch_pending`.

@pytest.fixture(autouse=True)
def patch_dependencies(module_mocker):
    # Mock do cliente Supabase
    mock_supabase_instance = MockSupabaseService()
    module_mocker.patch('fetch_pending.supabase_client_instance', mock_supabase_instance)
    module_mocker.patch('fetch_pending.core.supabase_service.supabase_client_instance', mock_supabase_instance) # Patch em caso de importação direta em core

    # Mock das configurações
    mock_settings_obj = MagicMock()
    mock_settings_obj.SUPABASE_URL = "http://mock-supabase.com"
    mock_settings_obj.SUPABASE_KEY = "mock-key"
    mock_settings_obj.IA_PROVIDER = "mock"
    module_mocker.patch('fetch_pending.settings', mock_settings_obj)
    module_mocker.patch('fetch_pending.core.config.settings', mock_settings_obj) # Patch em caso de importação direta em core

    # O script real tem `if not supabase_client_instance:`
    # Precisamos garantir que essa checagem funcione corretamente no mock.
    # Se `supabase_client_instance` for `None`, o script deve parar.
    # Nosso mock `MockSupabaseService` não é None, então isso deve funcionar.

    return mock_supabase_instance # Retorna o mock para que os testes possam configurá-lo

# --- Testes ---

@async_test
async def test_fetch_and_process_pending_success(self, patch_dependencies):
    """Testa o cenário de sucesso: comentários encontrados e atualizados."""
    mock_supabase = patch_dependencies # Recebe o mock injetado pelo fixture

    # Configura o retorno do mock para fetch_unprocessed_comments
    mock_supabase.fetch_unprocessed_comments_return_value = [
        {'id': 1, 'texto_bruto': 'Comentario 1', 'texto_limpo': 'Comentario 1 processado', 'organization_id': 'org1'},
        {'id': 2, 'texto_bruto': 'Comentario 2', 'texto_limpo': '', 'organization_id': 'org1'}, # Teste de fallback
    ]

    await fetch_and_process_pending()

    # Verifica se os métodos foram chamados corretamente
    assert mock_supabase.fetch_unprocessed_comments_call_count == 1
    assert mock_supabase.fetch_unprocessed_comments_kwargs['limit'] == 100

    assert mock_supabase.update_comment_classification_call_count == 2
    # Verifica as chamadas de atualização
    # O primeiro comentário tem texto_limpo, então deve ser usado.
    # O segundo comentário não tem texto_limpo, então texto_bruto deve ser usado.
    updates = mock_supabase.update_comment_classification_kwargs_list
    assert any(u['comment_id'] == '1' and u['data'] == {'processado_ia': True} for u in updates)
    assert any(u['comment_id'] == '2' and u['data'] == {'processado_ia': True} for u in updates)
    

@async_test
async def test_fetch_and_process_pending_no_comments(self, patch_dependencies):
    """Testa o cenário onde nenhum comentário pendente é encontrado."""
    mock_supabase = patch_dependencies
    mock_supabase.fetch_unprocessed_comments_return_value = [] # Nenhum comentário

    await fetch_and_process_pending()

    assert mock_supabase.fetch_unprocessed_comments_call_count == 1
    assert mock_supabase.update_comment_classification_call_count == 0 # Nenhuma atualização deve ocorrer

@async_test
async def test_fetch_and_process_pending_fetch_error(self, patch_dependencies):
    """Testa o tratamento de erro ao buscar comentários."""
    mock_supabase = patch_dependencies
    mock_supabase.raise_fetch_error = Exception("Erro de conexão ao buscar")

    # Redirecionar print para capturar a saída de erro
    with patch('builtins.print') as mock_print:
        await fetch_and_process_pending()

        assert mock_supabase.fetch_unprocessed_comments_call_count == 1
        assert mock_supabase.update_comment_classification_call_count == 0
        # Verifica se a mensagem de erro foi impressa
        mock_print.assert_any_call("❌ Erro fatal na execução do fetch_and_process_pending: Erro de conexão ao buscar")

@async_test
async def test_fetch_and_process_pending_update_error(self, patch_dependencies):
    """Testa o tratamento de erro ao atualizar um comentário."""
    mock_supabase = patch_dependencies
    mock_supabase.fetch_unprocessed_comments_return_value = [
        {'id': 1, 'texto_bruto': 'Comentario 1', 'texto_limpo': 'Comentario 1 processado'},
        {'id': 2, 'texto_bruto': 'Comentario 2', 'texto_limpo': 'Comentario 2 processado'},
    ]
    mock_supabase.raise_update_error = Exception("Erro ao atualizar no BD")

    with patch('builtins.print') as mock_print:
        await fetch_and_process_pending()

        assert mock_supabase.fetch_unprocessed_comments_call_count == 1
        assert mock_supabase.update_comment_classification_call_count == 2 # Deveria tentar atualizar ambos
        
        # Verifica se mensagens de erro para atualização foram impressas
        mock_print.assert_any_call("❌ Erro ao atualizar ID 1 no Supabase: Erro ao atualizar no BD")
        mock_print.assert_any_call("❌ Erro ao atualizar ID 2 no Supabase: Erro ao atualizar no BD")
        mock_print.assert_any_call("Falhas na atualização: 2") # Contagem de erros

@async_test
async def test_fetch_and_process_pending_missing_id(self, patch_dependencies):
    """Testa o cenário com registro sem ID."""
    mock_supabase = patch_dependencies
    mock_supabase.fetch_unprocessed_comments_return_value = [
        {'texto_bruto': 'Comentario sem ID', 'texto_limpo': 'Comentario processado'}, # Sem ID
        {'id': 2, 'texto_bruto': 'Comentario 2', 'texto_limpo': 'Comentario 2 processado'},
    ]

    with patch('builtins.print') as mock_print:
        await fetch_and_process_pending()

        assert mock_supabase.fetch_unprocessed_comments_call_count == 1
        assert mock_supabase.update_comment_classification_call_count == 1 # Apenas o segundo deve ser atualizado
        assert mock_supabase.update_comment_classification_kwargs_list[0]['comment_id'] == '2'
        
        # Verifica se o aviso de ID ausente foi impresso
        mock_print.assert_any_call("⚠️ Aviso: Registro sem ID encontrado, ignorando: {'texto_bruto': 'Comentario sem ID', 'texto_limpo': 'Comentario processado'}")
        assert any(u['comment_id'] == '2' for u in mock_supabase.update_comment_classification_kwargs_list)
        mock_print.assert_any_call("Falhas na atualização: 1") # Um registro ignorado conta como falha de atualização

@async_test
async def test_fetch_and_process_pending_empty_text_fields(self, patch_dependencies):
    """Testa o cenário onde texto_limpo e texto_bruto são vazios/null."""
    mock_supabase = patch_dependencies
    mock_supabase.fetch_unprocessed_comments_return_value = [
        {'id': 1, 'texto_bruto': '', 'texto_limpo': '', 'organization_id': 'org1'}, # Ambos vazios
        {'id': 2, 'texto_bruto': 'Comentario 2', 'texto_limpo': 'Comentario 2 processado', 'organization_id': 'org1'},
    ]

    await fetch_and_process_pending()

    assert mock_supabase.fetch_unprocessed_comments_call_count == 1
    assert mock_supabase.update_comment_classification_call_count == 1 # Apenas o segundo deve ser atualizado
    assert mock_supabase.update_comment_classification_kwargs_list[0]['comment_id'] == '2'

