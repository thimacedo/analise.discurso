import scrapy
import json
import os
from datetime import datetime

class InstagramSpider(scrapy.Spider):
    name = "instagram"
    
    def __init__(self, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.session_id = os.getenv("INSTAGRAM_SESSIONID")
        # App ID estÃ¡tico exigido pela API v1 do Instagram Web
        self.app_id = "936619743392459" 
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-IG-App-ID": self.app_id,
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": f"sessionid={self.session_id}"
        }
        
        try:
            with open('E:/projetos/sentinela-democratica/data/priority_queue.json', 'r') as f:
                self.targets = json.load(f)
        except:
            self.targets = ["lulaoficial", "bolsonarosp"]

    def start_requests(self):
        for username in self.targets:
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            # O Referer Ã© crucial para evitar o erro 400
            headers = self.headers.copy()
            headers["Referer"] = f"https://www.instagram.com/{username}/"
            
            yield scrapy.Request(
                url, 
                headers=headers, 
                callback=self.parse_profile, 
                meta={'username': username},
                dont_filter=True
            )

    def parse_profile(self, response):
        if response.status != 200:
            self.logger.error(f"❌ Falha no perfil {response.meta['username']} (Status {response.status})")
            return

        try:
            data = json.loads(response.text)
            user = data.get('data', {}).get('user', {})
            if not user: return

            yield {
                'type': 'profile',
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'profile_pic': user['profile_pic_url']
            }

            edges = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
            for edge in edges[:3]:
                node = edge['node']
                shortcode = node['shortcode']
                media_id = node['id']
                
                yield {
                    'type': 'post',
                    'id': media_id,
                    'shortcode': shortcode,
                    'owner_id': user['id'],
                    'timestamp': node['taken_at_timestamp']
                }

                # API de ComentÃ¡rios (Endpoint alternativo mais resiliente)
                comments_url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
                yield scrapy.Request(
                    comments_url, 
                    headers=self.headers, 
                    callback=self.parse_comments, 
                    meta={'post_shortcode': shortcode}
                )
        except Exception as e:
            self.logger.error(f"Erro no parse de {response.meta['username']}: {e}")

    def parse_comments(self, response):
        try:
            data = json.loads(response.text)
            comments = data.get('comments', [])
            for comment in comments[:50]:
                yield {
                    'type': 'comment',
                    'id': comment['pk'],
                    'text': comment['text'],
                    'owner_username': comment['user']['username'],
                    'timestamp': comment['created_at'],
                    'post_shortcode': response.meta['post_shortcode']
                }
        except Exception as e:
            self.logger.error(f"Erro nos comentÃ¡rios: {e}")
