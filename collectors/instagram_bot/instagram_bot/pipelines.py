import os
from supabase import create_client, Client
from instagram_bot.items import InstagramProfileItem, InstagramPostItem, InstagramCommentItem

class SupabasePipeline:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar definidos nas variáveis de ambiente.")
        self.supabase: Client = create_client(url, key)

    def process_item(self, item, spider):
        try:
            if isinstance(item, InstagramProfileItem):
                self.supabase.table("profiles").upsert(
                    data={
                        "user_id": str(item["user_id"]),
                        "username": item["username"],
                        "full_name": item.get("full_name", "")
                    }, 
                    on_conflict="user_id"
                ).execute()

            elif isinstance(item, InstagramPostItem):
                self.supabase.table("posts").upsert(
                    data={
                        "post_id": str(item["post_id"]),
                        "shortcode": item["shortcode"],
                        "owner_username": item["owner_username"],
                        "text": item.get("text", ""),
                        "timestamp": item["timestamp"]
                    }, 
                    on_conflict="post_id"
                ).execute()

            elif isinstance(item, InstagramCommentItem):
                self.supabase.table("comments").upsert(
                    data={
                        "comment_id": str(item["comment_id"]),
                        "post_shortcode": item["post_shortcode"],
                        "owner_username": item["owner_username"],
                        "text": item.get("text", ""),
                        "timestamp": item["timestamp"]
                    }, 
                    on_conflict="comment_id"
                ).execute()

        except Exception as e:
            spider.logger.error(f"Erro ao salvar no Supabase: {e} - Item: {item}")

        return item
