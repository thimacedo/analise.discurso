import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.config import settings
from supabase import create_client, Client

class DatabaseClient:
    def __init__(self):
        self.url = settings.SUPABASE_URL
        self.key = settings.SUPABASE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json"
        }
        self.client: Client = create_client(self.url, self.key) if self.url and self.key else None

    async def fetch_unprocessed_comments(self, limit: int = 200) -> List[Dict[str, Any]]:
        """Busca comentários que ainda não foram processados pela IA."""
        url = f"{self.url}/rest/v1/comentarios?processado_ia=not.eq.true&limit={limit}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
            return []

    async def fetch_all_data(self) -> List[Dict[str, Any]]:
        """Busca todos os comentários processados."""
        url = f"{self.url}/rest/v1/comentarios?select=*"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
            return []

    async def update_comment_classification(self, comment_id: str, data: Dict[str, Any]):
        """Atualiza a classificação de um único comentário."""
        url = f"{self.url}/rest/v1/comentarios?id=eq.{comment_id}"
        async with httpx.AsyncClient() as client:
            await client.patch(url, headers=self.headers, json=data)

    async def batch_update_comments(self, updates: List[Dict[str, Any]]):
        """
        Executa atualizações em lote. 
        Nota: O Supabase REST API não suporta batch PATCH nativo com IDs diferentes de forma trivial.
        Usaremos RPC ou enviaremos individualmente via pool de conexões se necessário.
        Para Diamond Edition, usaremos uma RPC customizada se disponível, ou loop otimizado.
        """
        # Se tivéssemos a RPC 'upsert_comentarios' seria ideal.
        # Por enquanto, loop assíncrono controlado.
        tasks = []
        for update in updates:
            comment_id = update.pop('id')
            tasks.append(self.update_comment_classification(comment_id, update))
        
        import asyncio
        await asyncio.gather(*tasks)

    async def upsert_daily_metrics(self, payload: Dict[str, Any]):
        """Salva ou atualiza métricas diárias via RPC."""
        url = f"{self.url}/rest/v1/rpc/upsert_metrica_diaria"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json=payload, headers=self.headers)
                return resp.status_code in [200, 201, 204]
            except Exception as e:
                print(f"⚠️ Erro RPC metrics: {e}")
                return False

    async def persist_coordinated_network(self, payload: Dict[str, Any]):
        """Persiste rede coordenada detectada."""
        url = f"{self.url}/rest/v1/redes_coordenadas"
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, headers=self.headers)

    async def create_active_alert(self, payload: Dict[str, Any]):
        """Cria um alerta ativo no sistema."""
        url = f"{self.url}/rest/v1/alertas_ativos"
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, headers=self.headers)

db_client = DatabaseClient()
