import scrapy
import json
from urllib.parse import urlencode

class InstagramCommentsSpider(scrapy.Spider):
    name = 'instagram_comments'
    
    custom_settings = {
        'CONCURRENT_REQUESTS': 1, # Instagram bane fácil, 1 por vez
    }
    
    def __init__(self, username='', sessionid='', max_posts=5, *args, **kwargs):
        super(InstagramCommentsSpider, self).__init__(*args, **kwargs)
        if not username or not sessionid:
            raise ValueError("Username e SessionID são obrigatórios.")
            
        self.username = username
        self.sessionid = sessionid
        self.max_posts = int(max_posts)
        self.app_id = "936619743392459"
        self.base_url = "https://www.instagram.com"
        
    def start_requests(self):
        """1. Busca o ID do usuário e os posts recentes."""
        url = f"{self.base_url}/api/v1/users/web_profile_info/?username={self.username}"
        headers = {
            "X-IG-App-ID": self.app_id,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        cookies = {"sessionid": self.sessionid}
        
        yield scrapy.Request(
            url, 
            callback=self.parse_profile, 
            headers=headers, 
            cookies=cookies,
            dont_filter=True
        )
        
    def parse_profile(self, response):
        """2. Extrai os Media IDs dos posts e solicita comentários."""
        try:
            data = json.loads(response.text)
            user = data.get("data", {}).get("user", {})
            edges = user.get("edge_owner_to_timeline_media", {}).get("edges", [])
            
            for edge in edges[:self.max_posts]:
                node = edge.get("node", {})
                media_id = node.get("id")
                shortcode = node.get("shortcode")
                
                if media_id:
                    yield from self.request_comments(media_id, shortcode)
                    
        except Exception as e:
            self.logger.error(f"Erro ao parsear perfil: {e}")
            
    def request_comments(self, media_id, shortcode):
        """3. Faz a paginação dos comentários."""
        url = f"{self.base_url}/api/v1/media/{media_id}/comments/"
        headers = {
            "X-IG-App-ID": self.app_id,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        cookies = {"sessionid": self.sessionid}
        
        yield scrapy.Request(
            url,
            callback=self.parse_comments,
            headers=headers,
            cookies=cookies,
            meta={"shortcode": shortcode, "media_id": media_id},
            dont_filter=True
        )
        
    def parse_comments(self, response):
        """4. Extrai os comentários e faz paginação se houver next_max_id."""
        try:
            data = json.loads(response.text)
            shortcode = response.meta.get("shortcode")
            raw_comments = data.get("comments", [])
            
            for c in raw_comments:
                yield {
                    "id": c.get("pk"),
                    "text": c.get("text"),
                    "ownerUsername": c.get("user", {}).get("username"),
                    "timestamp": c.get("created_at"),
                    "shortcode": shortcode,
                    "target": self.username
                }
                
            # Paginação (Se o Instagram retornar next_max_id, busca a próxima página)
            next_max_id = data.get("next_max_id")
            if next_max_id:
                media_id = response.meta.get("media_id")
                url = f"{self.base_url}/api/v1/media/{media_id}/comments/?max_id={next_max_id}"
                headers = {
                    "X-IG-App-ID": self.app_id,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                cookies = {"sessionid": self.sessionid}
                
                yield scrapy.Request(
                    url,
                    callback=self.parse_comments,
                    headers=headers,
                    cookies=cookies,
                    meta={"shortcode": shortcode, "media_id": media_id},
                    dont_filter=True
                )
                
        except Exception as e:
            self.logger.error(f"Erro ao parsear comentários: {e}")
