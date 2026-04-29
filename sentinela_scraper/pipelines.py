import os
import httpx
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
            "Prefer": "resolution=merge-duplicates"
        }

    def process_item(self, item, spider):
        if not self.url or not self.key:
            spider.logger.error("❌ SUPABASE_URL ou SUPABASE_KEY não configurados")
            return item

        item_type = item.pop('type')
        
        # Mapeamento corrigido conforme introspecção do Supabase
        if item_type == 'profile':
            table = "candidatos"
            payload = {
                "username": item['username'],
                "nome_completo": item.get('full_name', ''),
                "bio": item.get('bio', ''),
                "seguidores": item.get('seguidores', 0),
                "status_monitoramento": "ATIVO"
            }
        elif item_type == 'comment':
            table = "comentarios"
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
        else:
            # Ignora 'post' pois a tabela não existe no schema v18.5
            return item
        
        try:
            with httpx.Client(timeout=10.0) as client:
                # Usamos POST com resolution=merge-duplicates (conforme configurado no init)
                resp = client.post(f"{self.url}/rest/v1/{table}", json=payload, headers=self.headers)
                if resp.status_code not in [200, 201]:
                    spider.logger.error(f"❌ Erro Supabase ({table}): {resp.status_code} - {resp.text}")
        except Exception as e:
            spider.logger.error(f"🔥 Falha de conexão Supabase: {e}")

    def close_spider(self, spider):
        pass
