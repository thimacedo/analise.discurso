import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client
from instagram_bot.items import InstagramProfileItem, InstagramPostItem, InstagramCommentItem

load_dotenv()

class SupabasePipeline:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        if not self.url or not self.key:
            logging.error("Supabase URL or Key not found in environment variables.")
            return
        self.supabase: Client = create_client(self.url, self.key)

    def process_item(self, item, spider):
        if not self.url or not self.key:
            return item

        table_name = ""
        if isinstance(item, InstagramProfileItem):
            table_name = "instagram_profiles"
        elif isinstance(item, InstagramPostItem):
            table_name = "instagram_posts"
        elif isinstance(item, InstagramCommentItem):
            table_name = "instagram_comments"

        if table_name:
            data = dict(item)
            data['updated_at'] = datetime.utcnow().isoformat()
            
            try:
                # Upsert using 'on_conflict' if supported by the client version or direct RPC if needed.
                # The supabase-py client uses postgrest-py which supports upsert with primary key conflict resolution by default.
                self.supabase.table(table_name).upsert(data, on_conflict="id").execute()
            except Exception as e:
                logging.error(f"Error inserting into Supabase ({table_name}): {e}")

        return item
