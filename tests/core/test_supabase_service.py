import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

# Assume that core.supabase_service is correctly importable and settings are available
# If not, these tests might fail or need adjustment based on the actual project structure and mocking strategy.
from core.supabase_service import SupabaseService
from core.config import settings

# Mocking Supabase client and httpx client for isolation
@pytest.fixture
def mock_supabase_service():
    # Mock the create_client call to return a mock client
    mock_client = MagicMock(spec=SupabaseService)
    mock_client.url = "http://mock-url.com"
    mock_client.key = "mock-key"
    mock_client.headers = {"apikey": "mock-key", "Authorization": "Bearer mock-key", "Content-Type": "application/json"}
    mock_client.client = MagicMock() # Mock the actual Supabase client object
    mock_client.http_client = MagicMock(spec=httpx.AsyncClient) # Mock the httpx client
    return mock_client

@pytest.fixture
def mock_settings():
    mock_settings = MagicMock()
    mock_settings.SUPABASE_URL = "http://mock-url.com"
    mock_settings.SUPABASE_KEY = "mock-key"
    return mock_settings

# Patching settings and create_client globally for tests
@pytest.fixture(autouse=True)
def patch_globals(mock_settings):
    with patch('core.supabase_service.settings', mock_settings, create=True):
        with patch('core.supabase_service.create_client', return_value=MagicMock()) as mock_create_client:
            yield mock_create_client

# --- Test Cases for SupabaseService ---

@pytest.mark.asyncio
async def test_fetch_unprocessed_comments_success(mock_supabase_service):
    mock_supabase_service.http_client.get.return_value = AsyncMock(status_code=200, json=lambda: [{"id": 1, "text": "comment1"}])
    comments = await mock_supabase_service.fetch_unprocessed_comments(limit=10)
    assert len(comments) == 1
    assert comments[0]["id"] == 1

@pytest.mark.asyncio
async def test_fetch_unprocessed_comments_http_error(mock_supabase_service):
    mock_response = AsyncMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_supabase_service.http_client.get.side_effect = httpx.HTTPStatusError("400 Client Error", request=httpx.Request("GET", "http://mock-url.com"), response=mock_response)
    comments = await mock_supabase_service.fetch_unprocessed_comments()
    assert comments == []

@pytest.mark.asyncio
async def test_fetch_unprocessed_comments_request_error(mock_supabase_service):
    mock_supabase_service.http_client.get.side_effect = httpx.RequestError("Network error")
    comments = await mock_supabase_service.fetch_unprocessed_comments()
    assert comments == []

@pytest.mark.asyncio
async def test_fetch_all_data_success(mock_supabase_service):
    mock_supabase_service.http_client.get.return_value = AsyncMock(status_code=200, json=lambda: [{"id": 1, "text": "comment1"}])
    data = await mock_supabase_service.fetch_all_data()
    assert len(data) == 1
    assert data[0]["id"] == 1

@pytest.mark.asyncio
async def test_update_comment_classification_success(mock_supabase_service):
    mock_supabase_service.http_client.patch.return_value = AsyncMock(status_code=204)
    await mock_supabase_service.update_comment_classification("1", {"category_ia": "spam"})
    mock_supabase_service.http_client.patch.assert_called_once()

@pytest.mark.asyncio
async def test_batch_update_comments_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.upsert.return_value.execute.return_value = None
    updates = [{"id": 1, "processado_ia": True}, {"id": 2, "processado_ia": True}]
    await mock_supabase_service.batch_update_comments(updates)
    mock_supabase_service.client.table.assert_called_once_with('comentarios')
    mock_supabase_service.client.table.return_value.upsert.assert_called_once_with(updates)

@pytest.mark.asyncio
async def test_batch_update_comments_no_updates(mock_supabase_service):
    await mock_supabase_service.batch_update_comments([])
    mock_supabase_service.client.table.assert_not_called()

@pytest.mark.asyncio
async def test_batch_update_ad_classification_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.upsert.return_value = None
    updates = [{"id": 1, "processado_ia": True}, {"id": 2, "processado_ia": True}]
    await mock_supabase_service.batch_update_ad_classification(updates)
    mock_supabase_service.client.table.assert_called_once_with('anuncios')
    mock_supabase_service.client.table.return_value.upsert.assert_called_once_with(updates)

@pytest.mark.asyncio
async def test_upsert_daily_metrics_success(mock_supabase_service):
    mock_supabase_service.http_client.post.return_value = AsyncMock(status_code=200)
    payload = {"metric_name": "cpu_usage", "value": 0.5}
    result = await mock_supabase_service.upsert_daily_metrics(payload)
    assert result is True
    mock_supabase_service.http_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_upsert_daily_metrics_rpc_error(mock_supabase_service):
    mock_response = AsyncMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_supabase_service.http_client.post.side_effect = httpx.HTTPStatusError("500 Server Error", request=httpx.Request("POST", "http://mock-url.com"), response=mock_response)
    payload = {"metric_name": "cpu_usage", "value": 0.5}
    result = await mock_supabase_service.upsert_daily_metrics(payload)
    assert result is False

@pytest.mark.asyncio
async def test_persist_coordinated_network_success(mock_supabase_service):
    mock_supabase_service.http_client.post.return_value = AsyncMock(status_code=200)
    payload = {"network_data": "some_data"}
    await mock_supabase_service.persist_coordinated_network(payload)
    mock_supabase_service.http_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_create_active_alert_success(mock_supabase_service):
    mock_supabase_service.http_client.post.return_value = AsyncMock(status_code=200)
    payload = {"alert_type": "high_cpu", "details": "High CPU usage detected"}
    await mock_supabase_service.create_active_alert(payload)
    mock_supabase_service.http_client.post.assert_called_once()

@pytest.mark.asyncio
async def test_fetch_targets_needing_repericia_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"username": "user1"}, {"username": "user2"}]
    usernames = await mock_supabase_service.fetch_targets_needing_repericia()
    assert usernames == ["user1", "user2"]
    mock_supabase_service.client.table.assert_called_once_with('candidatos')

@pytest.mark.asyncio
async def test_fetch_targets_needing_repericia_no_column(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("column needs_re_pericia does not exist")
    usernames = await mock_supabase_service.fetch_targets_needing_repericia()
    assert usernames == []

@pytest.mark.asyncio
async def test_reset_target_comments_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{"id": 101}, {"id": 102}]
    mock_supabase_service.client.table.return_value.update.return_value.in_.return_value.execute.return_value = None
    await mock_supabase_service.reset_target_comments("user1")
    mock_supabase_service.client.table.assert_any_call('comentarios')
    mock_supabase_service.client.table.return_value.update.assert_called_once()

@pytest.mark.asyncio
async def test_reset_target_comments_no_comments(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.data = []
    await mock_supabase_service.reset_target_comments("user1")
    mock_supabase_service.client.table.assert_called_once_with('comentarios')
    # update should not be called if no comments are found
    mock_supabase_service.client.table.return_value.update.assert_not_called()

@pytest.mark.asyncio
async def test_mark_repericia_complete_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.update.return_value.eq.return_value.execute.return_value = None
    await mock_supabase_service.mark_repericia_complete("user1")
    mock_supabase_service.client.table.assert_called_once_with('candidatos')
    mock_supabase_service.client.table.return_value.update.assert_called_once_with({'needs_re_pericia': False})

@pytest.mark.asyncio
async def test_persist_ad_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.upsert.return_value = None
    ad_data = {"ad_id": "ad123", "campaign_id": "c1"}
    await mock_supabase_service.persist_ad(ad_data)
    mock_supabase_service.client.table.assert_called_once_with('anuncios')
    mock_supabase_service.client.table.return_value.upsert.assert_called_once_with(ad_data, on_conflict='ad_id')

@pytest.mark.asyncio
async def test_persist_ads_batch_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.upsert.return_value = None
    ads_data = [{"ad_id": "ad123", "campaign_id": "c1"}, {"ad_id": "ad456", "campaign_id": "c2"}]
    await mock_supabase_service.persist_ads_batch(ads_data)
    mock_supabase_service.client.table.assert_called_once_with('anuncios')
    mock_supabase_service.client.table.return_value.upsert.assert_called_once_with(ads_data, on_conflict='ad_id')

@pytest.mark.asyncio
async def test_fetch_unprocessed_ads_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = [{"id": 1, "ad_id": "ad123"}]
    ads = await mock_supabase_service.fetch_unprocessed_ads(limit=10)
    assert len(ads) == 1
    assert ads[0]["ad_id"] == "ad123"

@pytest.mark.asyncio
async def test_fetch_unprocessed_ads_no_column(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.limit.return_value.execute.side_effect = Exception("column mined does not exist")
    ads = await mock_supabase_service.fetch_unprocessed_ads()
    assert ads == []

@pytest.mark.asyncio
async def test_update_ad_classification_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.update.return_value.eq.return_value.execute.return_value = None
    data = {"processado_ia": True, "classification": "safe"}
    await mock_supabase_service.update_ad_classification("ad123", data)
    mock_supabase_service.client.table.assert_called_once_with('anuncios')
    mock_supabase_service.client.table.return_value.update.assert_called_once_with(data)
    mock_supabase_service.client.table.return_value.eq.assert_called_once_with('ad_id', "ad123")

@pytest.mark.asyncio
async def test_persist_dossier_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.insert.return_value.execute.return_value.data = [{"id": 1, "hash_integridade": "hash123"}]
    dossier_data = {"candidato_id": "cand1", "hash_integridade": "hash123"}
    result = await mock_supabase_service.persist_dossier(dossier_data)
    assert result[0]["id"] == 1
    mock_supabase_service.client.table.assert_called_once_with('dossies')
    mock_supabase_service.client.table.return_value.insert.assert_called_once_with(dossier_data)

@pytest.mark.asyncio
async def test_fetch_dossier_history_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [{"id": 1, "data_geracao": "2023-01-01"}]
    history = await mock_supabase_service.fetch_dossier_history("cand1")
    assert len(history) == 1
    assert history[0]["id"] == 1

@pytest.mark.asyncio
async def test_fetch_unmined_comments_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.side_effect = [
        AsyncMock(return_value=AsyncMock(data=[{"id": 1, "text": "comment1"}])), # First eq for processado_ia=True
        AsyncMock(return_value=AsyncMock(data=[{"id": 1, "text": "comment1"}]))  # Second eq for mined=False
    ]
    comments = await mock_supabase_service.fetch_unmined_comments(limit=10)
    assert len(comments) == 1
    assert comments[0]["id"] == 1

@pytest.mark.asyncio
async def test_fetch_unmined_comments_no_mined_column(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.side_effect = [
        Exception("column mined does not exist"), # First eq for processado_ia=True
        AsyncMock(return_value=AsyncMock(data=[{"id": 1, "text": "comment1"}]))  # Fallback eq for processado_ia=True
    ]
    comments = await mock_supabase_service.fetch_unmined_comments(limit=10)
    assert len(comments) == 1
    assert comments[0]["id"] == 1

@pytest.mark.asyncio
async def test_fetch_unmined_ads_success(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.side_effect = [
        AsyncMock(return_value=AsyncMock(data=[{"id": 1, "ad_id": "ad123"}])), # First eq for processado_ia=True
        AsyncMock(return_value=AsyncMock(data=[{"id": 1, "ad_id": "ad123"}]))  # Second eq for mined=False
    ]
    ads = await mock_supabase_service.fetch_unmined_ads(limit=10)
    assert len(ads) == 1
    assert ads[0]["ad_id"] == "ad123"

@pytest.mark.asyncio
async def test_fetch_unmined_ads_no_mined_column(mock_supabase_service):
    mock_supabase_service.client.table.return_value.select.return_value.eq.side_effect = [
        Exception("column mined does not exist"), # First eq for processado_ia=True
        AsyncMock(return_value=AsyncMock(data=[{"id": 1, "ad_id": "ad123"}]))  # Fallback eq for processado_ia=True
    ]
    ads = await mock_supabase_service.fetch_unmined_ads(limit=10)
    assert len(ads) == 1
    assert ads[0]["ad_id"] == "ad123"
