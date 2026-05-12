
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SupabasePipeline:
    def __init__(self):
        url = os.getenv("SUPABASE_URL", "")
        if url and not url.startswith("http"):
            url = f"https://{url}"
        self.url = url
        
        self.key = os.getenv("SUPABASE_KEY")
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

    def process_item(self, item, spider):
        if not self.url or not self.key:
            spider.logger.error("❌ SUPABASE_URL ou SUPABASE_KEY não configurados")
            return item

        item_type = item.get('type')
        
        if item_type == 'profile':
            self._update_profile(item, spider)
        elif item_type == 'comment':
            self._insert_comment(item, spider)
        
        return item

    def _update_profile(self, item, spider):
        """Atualiza dados do perfil (candidatos) usando PATCH."""
        url = f"{self.url}/rest/v1/candidatos"
        payload = {
            "nome_completo": item.get('full_name', ''),
            "bio": item.get('bio', ''),
            "seguidores": item.get('seguidores', 0),
            "last_scraped_at": datetime.now().isoformat()
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                # PATCH com filtro no username
                resp = client.patch(
                    f"{url}?username=eq.{item['username']}", 
                    json=payload, 
                    headers=self.headers
                )
                if resp.status_code not in [200, 201, 204]:
                    spider.logger.error(f"❌ Erro ao atualizar perfil {item['username']}: {resp.status_code} - {resp.text}")
        except Exception as e:
            spider.logger.error(f"🔥 Falha de conexão Supabase (profile): {e}")

    def _insert_comment(self, item, spider):
        """Insere comentário no Supabase. Ignora duplicatas (409)."""
        url = f"{self.url}/rest/v1/comentarios"
        
        # Conversão de timestamp Unix para ISO
        timestamp = item.get('timestamp')
        data_coleta = datetime.fromtimestamp(timestamp).isoformat() if timestamp else datetime.now().isoformat()

        payload = {
            "id_externo": str(item['id']),
            "candidato_id": item['candidato_username'],
            "post_id": str(item['post_shortcode']),
            "autor_username": item['owner_username'],
            "texto_bruto": item['text'],
            "likes": item.get('likes_count', 0),
            "data_coleta": data_coleta,
            "processado_ia": False
        }
        
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, json=payload, headers=self.headers)
                
                if resp.status_code == 409:
                    # Duplicata é esperada e ignorada silenciosamente
                    pass
                elif resp.status_code not in [200, 201, 204]:
                    spider.logger.error(f"❌ Erro ao inserir comentário {item['id']}: {resp.status_code} - {resp.text}")
        except Exception as e:
            spider.logger.error(f"🔥 Falha de conexão Supabase (comment): {e}")

    def close_spider(self, spider):
        pass
