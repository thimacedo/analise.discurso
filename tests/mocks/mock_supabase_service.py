# tests/mocks/mock_supabase_service.py
import asyncio
from typing import List, Dict, Any
from unittest.mock import MagicMock, AsyncMock

class MockSupabaseService:
    def __init__(self, *args, **kwargs):
        self.client = MagicMock()
        self.http_client = MagicMock()
        self.fetch_unprocessed_comments_return_value = []
        self.fetch_unprocessed_comments_call_count = 0

    async def fetch_unprocessed_comments(self, limit: int = 100, org_id: str = None) -> List[Dict[str, Any]]:
        self.fetch_unprocessed_comments_call_count += 1
        return self.fetch_unprocessed_comments_return_value

    async def fetch_all_data(self) -> List[Dict[str, Any]]:
        return []

    async def update_comment_classification(self, comment_id: str, data: Dict[str, Any]):
        pass

    async def batch_update_comments(self, updates: List[Dict[str, Any]]):
        pass

    async def batch_update_ad_classification(self, updates: List[Dict[str, Any]]):
        pass

    async def upsert_daily_metrics(self, payload: Dict[str, Any]) -> bool:
        return True

    async def persist_coordinated_network(self, payload: Dict[str, Any]):
        pass

    async def create_active_alert(self, payload: Dict[str, Any]):
        pass

    async def fetch_targets_needing_repericia(self) -> List[str]:
        return []

    async def reset_target_comments(self, username: str):
        pass

    async def mark_repericia_complete(self, username: str):
        pass

    async def persist_ad(self, ad_data: Dict[str, Any]):
        pass

    async def persist_ads_batch(self, ads_data: List[Dict[str, Any]]):
        pass

    async def fetch_unprocessed_ads(self, limit: int = 100) -> List[Dict[str, Any]]:
        return []

    async def update_ad_classification(self, ad_id: str, data: Dict[str, Any]):
        pass

    async def persist_dossier(self, dossier_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return []

    async def fetch_dossier_history(self, candidato_id: str) -> List[Dict[str, Any]]:
        return []

    async def fetch_unmined_comments(self, limit: int = 100) -> List[Dict[str, Any]]:
        return []

    async def fetch_unmined_ads(self, limit: int = 100) -> List[Dict[str, Any]]:
        return []

    async def close(self):
        pass

supabase_client_instance = MockSupabaseService()
