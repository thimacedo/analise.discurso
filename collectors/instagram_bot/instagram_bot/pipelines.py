import os
import httpx
import json
import logging
from instagram_bot.items import InstagramProfileItem, InstagramPostItem, InstagramCommentItem

class SupabasePipeline:
    """
    Pipeline de Alta Performance via REST direto (sem dependências quebradas).
    Utiliza httpx para realizar UPSERTS atômicos no Supabase.
    """
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY ausentes no .env")
        
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }

    def process_item(self, item, spider):
        table = ""
        data = {}
        
        if isinstance(item, InstagramProfileItem):
            table = "profiles"
            data = {
                "user_id": str(item["user_id"]),
                "username": item["username"],
                "full_name": item.get("full_name", "")
            }
        elif isinstance(item, InstagramPostItem):
            table = "posts"
            data = {
                "post_id": str(item["post_id"]),
                "shortcode": item["shortcode"],
                "owner_username": item["owner_username"],
                "text": item.get("text", ""),
                "timestamp": item["timestamp"]
            }
        elif isinstance(item, InstagramCommentItem):
            table = "comments"
            data = {
                "comment_id": str(item["comment_id"]),
                "post_shortcode": item["post_shortcode"],
                "owner_username": item["owner_username"],
                "text": item.get("text", ""),
                "timestamp": item["timestamp"]
            }

        if table:
            try:
                # Upsert via POST com header Prefer: resolution=merge-duplicates (Nativo PostgREST)
                endpoint = f"{self.url}/rest/v1/{table}"
                with httpx.Client() as client:
                    r = client.post(endpoint, json=data, headers=self.headers)
                    if r.status_code not in [200, 201]:
                        spider.logger.error(f"❌ Erro Supabase ({table}): {r.text}")
                    else:
                        print(f"📊 [PIPELINE] Item smonitorado com sucesso em {table}")
            except Exception as e:
                spider.logger.error(f"⚠️ Erro de rede no Pipeline: {e}")

        return item
