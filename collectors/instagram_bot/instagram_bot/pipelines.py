import os
import httpx
from datetime import datetime
from instagram_bot.items import InstagramBotItem

class SupabasePipeline:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

    def process_item(self, item, spider):
        if not isinstance(item, InstagramBotItem):
            return item

        table = ""
        data = {}
        item_type = item.get("item_type")
        
        if item_type == "profile":
            table = "profiles"
            data = {
                "user_id": str(item.get("user_id")),
                "username": item.get("username"),
                "full_name": item.get("full_name", "")
            }
        elif item_type == "post":
            table = "posts"
            data = {
                "post_id": str(item.get("post_id")),
                "shortcode": item.get("shortcode"),
                "owner_username": item.get("owner_username"),
                "text": item.get("text", ""),
                "timestamp": int(item.get("timestamp")) if item.get("timestamp") else None
            }
        elif item_type == "comment":
            table = "comments"
            data = {
                "comment_id": str(item.get("comment_id")),
                "post_shortcode": item.get("post_shortcode"),
                "owner_username": item.get("owner_username"),
                "text": item.get("text", ""),
                "timestamp": int(item.get("timestamp")) if item.get("timestamp") else None
            }

        if table and data:
            self.send_to_supabase(table, data, spider)

        return item

    def send_to_supabase(self, table, data, spider):
        endpoint = f"{self.url}/rest/v1/{table}"
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(endpoint, json=data, headers=self.headers)
                if resp.status_code not in [200, 201]:
                    spider.logger.error(f"Erro Supabase ({resp.status_code}) na tabela {table}: {resp.text}")
        except Exception as e:
            spider.logger.error(f"Falha na conexão com Supabase ({table}): {e}")
