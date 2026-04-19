import os
import time
import json
import sqlite3
from datetime import datetime
from apify_client import ApifyClient
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class ApifyFullScraper:
    def __init__(self):
        self.api_token = os.getenv("APIFY_API_TOKEN")
        if not self.api_token:
            # Fallback for the token found in apis.txt if not in .env
            self.api_token = ""
        
        self.client = ApifyClient(self.api_token)
        self.db_file = "odio_politica.db"
        self.profiles_file = os.path.join("data", "perfis_monitorados.json")

    def get_profiles(self):
        if not os.path.exists(self.profiles_file):
            print(f"❌ Erro: {self.profiles_file} não encontrado.")
            return []
        with open(self.profiles_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_full_scrape(self, limit_profiles=None, posts_per_profile=3, comments_per_post=100):
        profiles = self.get_profiles()
        if not profiles: return
        
        if limit_profiles:
            profiles = profiles[:limit_profiles]
            
        print(f"🚀 Iniciando raspagem FULL via Apify para {len(profiles)} perfis...")
        
        stats = {
            "start_time": datetime.now().isoformat(),
            "profiles_attempted": 0,
            "profiles_success": 0,
            "posts_scanned": 0,
            "comments_collected": 0,
            "errors": []
        }

        for profile in profiles:
            username = profile["username"]
            stats["profiles_attempted"] += 1
            print(f"\n📸 Processando @{username}...")
            
            try:
                # 1. Coletar Posts
                run_input = {
                    "directUrls": [f"https://www.instagram.com/{username}/"],
                    "resultsType": "posts",
                    "resultsLimit": posts_per_profile,
                    "searchLimit": 1,
                    "proxy": {"useApifyProxy": True}
                }
                
                print(f"   Buscando últimos {posts_per_profile} posts...")
                run = self.client.actor("apify/instagram-scraper").call(run_input=run_input)
                items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
                
                if not items:
                    print(f"   ⚠️ Nenhum post encontrado para @{username}.")
                    continue
                
                stats["profiles_success"] += 1
                
                for item in items:
                    shortcode = item.get("shortcode")
                    if not shortcode: continue
                    
                    stats["posts_scanned"] += 1
                    print(f"   💬 Coletando até {comments_per_post} comentários do post {shortcode}...")
                    
                    # 2. Coletar Comentários para cada Post
                    comment_input = {
                        "directUrls": [f"https://www.instagram.com/p/{shortcode}/"],
                        "resultsType": "comments",
                        "resultsLimit": comments_per_post,
                        "proxy": {"useApifyProxy": True}
                    }
                    
                    comment_run = self.client.actor("apify/instagram-scraper").call(run_input=comment_input)
                    comments = list(self.client.dataset(comment_run["defaultDatasetId"]).iterate_items())
                    
                    # 3. Salvar no Banco
                    self.save_to_db(username, shortcode, comments)
                    stats["comments_collected"] += len(comments)
                    print(f"   ✅ {len(comments)} comentários salvos.")

            except Exception as e:
                error_msg = f"Erro em @{username}: {str(e)}"
                print(f"   ❌ {error_msg}")
                stats["errors"].append(error_msg)
                continue

        stats["end_time"] = datetime.now().isoformat()
        self.log_stats(stats)
        print("\n🏆 RASPAGEM COMPLETA CONCLUÍDA!")
        return stats

    def save_to_db(self, username, post_id, comments):
        # DESTINO: SUPABASE CLOUD
        headers = {
            "apikey": os.getenv("SUPABASE_KEY"),
            "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        
        data_to_send = []
        now = datetime.now().isoformat()
        investigator_id = "66f853ed-c42b-43d4-bcc3-23f05b2c44e9"
        
        for c in comments:
            data_to_send.append({
                "id_externo": str(c.get("id")),
                "candidato_id": username,
                "post_id": post_id,
                "autor_username": c.get("ownerUsername"),
                "texto_bruto": c.get("text"),
                "data_coleta": now,
                "data_publicacao": c.get("timestamp"),
                "likes": c.get("likesCount", 0),
                "user_id": investigator_id
            })

        if data_to_send:
            url = f"{os.getenv('SUPABASE_URL')}/rest/v1/comentarios"
            try:
                import httpx
                response = httpx.post(url, json=data_to_send, headers=headers)
                if response.status_code not in [200, 201]:
                    print(f"      ⚠️ Erro Supabase: {response.text}")
            except Exception as e:
                print(f"      ⚠️ Falha de rede: {e}")

    def log_stats(self, run_stats):
        log_file = "extraction_stats_log.json"
        all_logs = []
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                try:
                    old_data = json.load(f)
                    if isinstance(old_data, list): all_logs = old_data
                    else: all_logs = [old_data]
                except: pass
        
        run_stats["method"] = "apify_full_scraper"
        all_logs.append(run_stats)
        
        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(all_logs, f, indent=4)

if __name__ == "__main__":
    # Teste com 2 perfis primeiro para validar o custo/tempo
    scraper = ApifyFullScraper()
    scraper.run_full_scrape(limit_profiles=2, posts_per_profile=2, comments_per_post=50)
