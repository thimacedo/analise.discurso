import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class SupabasePipeline:
    def __init__(self):
        # Garante que a URL tenha o protocolo correto
        url = os.getenv("SUPABASE_URL", "")
        if url and not url.startswith("http"):
            url = f"https://{url}"
        self.url = url
        
        self.key = os.getenv("SUPABASE_KEY")
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

    def process_item(self, item, spider):
        if not self.url or not self.key:
            spider.logger.error("❌ SUPABASE_URL ou SUPABASE_KEY nÃ£o configurados no .env")
            return item

        item_type = item.pop('type')
        table_map = {
            'profile': 'candidatos',
            'post': 'posts',
            'comment': 'comentarios'
        }
        
        table = table_map.get(item_type)
        if not table: return item

        # Mapeamento de campos para compatibilidade com o schema atual
        payload = item.copy()
        if item_type == 'profile':
            payload = {
                "id": item['id'],
                "username": item['username'],
                "nome_completo": item.get('full_name', ''),
                "status_monitoramento": "Ativo"
            }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(f"{self.url}/rest/v1/{table}", json=payload, headers=self.headers)
                if resp.status_code not in [200, 201]:
                    spider.logger.error(f"❌ Erro Supabase ({table}): {resp.status_code} - {resp.text}")
        except Exception as e:
            spider.logger.error(f"🔥 Falha de conexÃ£o Supabase: {e}")

        return item
