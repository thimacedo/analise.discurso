# tests/mocks/mock_supabase_service.py
import asyncio
from typing import List, Dict, Any

class MockSupabaseService:
    def __init__(self, *args, **kwargs):
        self.fetch_unprocessed_comments_return_value = []
        self.update_comment_classification_results = []
        self.fetch_unprocessed_comments_call_count = 0
        self.update_comment_classification_call_count = 0
        self.fetch_unprocessed_comments_kwargs = {}
        self.update_comment_classification_kwargs_list = []

    async def fetch_unprocessed_comments(self, limit: int = 100, org_id: str = None) -> List[Dict[str, Any]]:
        self.fetch_unprocessed_comments_call_count += 1
        self.fetch_unprocessed_comments_kwargs = {'limit': limit, 'org_id': org_id}
        print(f"[MockSupabaseService] fetch_unprocessed_comments called with limit={limit}, org_id={org_id}")
        await asyncio.sleep(0.01) # Simular delay de rede
        return self.fetch_unprocessed_comments_return_value

    async def update_comment_classification(self, comment_id: str, data: Dict[str, Any]):
        self.update_comment_classification_call_count += 1
        self.update_comment_classification_kwargs_list.append({'comment_id': comment_id, 'data': data})
        print(f"[MockSupabaseService] update_comment_classification called for {comment_id} with data: {data}")
        await asyncio.sleep(0.01) # Simular delay de rede
        # Não lança exceção por padrão, a menos que configurado para isso

    async def close(self):
        # Mock close method if needed
        pass

# Instância mock global para ser usada no teste
supabase_client_instance = MockSupabaseService()
