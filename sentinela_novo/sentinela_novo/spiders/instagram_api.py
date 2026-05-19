import scrapy
import json
from datetime import datetime

class InstagramCommentItem(scrapy.Item):
    comment_id = scrapy.Field()
    post_shortcode = scrapy.Field()
    ownerUsername = scrapy.Field()
    text = scrapy.Field()
    created_at = scrapy.Field()
    like_count = scrapy.Field()
    candidato_id = scrapy.Field()
    tier_used = scrapy.Field()
    scraped_at = scrapy.Field()

class InstagramAPISpider(scrapy.Spider):
    """
    Tier 1: API GraphQL do Instagram (SEM Playwright)
    """
    name = 'instagram_api'
    allowed_domains = ['instagram.com']
    
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 3,
        'COOKIES_ENABLED': True,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 2,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429],
    }
    
    def __init__(self, username='', sessionid='', max_posts=5, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = username
        self.sessionid = sessionid
        self.max_posts = int(max_posts)
        self.user_id = None
        
    def start_requests(self):
        """Obtém dados do perfil via API."""
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={self.username}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://www.instagram.com/{self.username}/',
        }
        
        yield scrapy.Request(
            url=url,
            headers=headers,
            cookies={'sessionid': self.sessionid},
            callback=self.parse_profile,
            dont_filter=True
        )
    
    def parse_profile(self, response):
        """Extrai user_id e posts."""
        try:
            data = json.loads(response.text)
            user_data = data.get('data', {}).get('user', {})
            
            self.user_id = user_data.get('id')
            if not self.user_id:
                self.logger.error("❌ Falha ao obter user_id")
                return
            
            posts = user_data.get('edge_owner_to_timeline_media', {}).get('edges', [])[:self.max_posts]
            self.logger.info(f"✅ Encontrados {len(posts)} posts para @{self.username}")
            
            for post in posts:
                shortcode = post.get('node', {}).get('shortcode')
                if shortcode:
                    yield from self.fetch_post_comments(shortcode)
                    
        except Exception as e:
            self.logger.error(f"❌ Erro ao parsear perfil: {e}")
    
    def fetch_post_comments(self, shortcode):
        """Busca comentários via GraphQL."""
        query_hash = 'bc3296d1ce80a24b1b6e40b1e72903f5'
        
        variables = {
            "shortcode": shortcode,
            "first": 50,
        }
        
        url = f"https://www.instagram.com/graphql/query/?query_hash={query_hash}&variables={json.dumps(variables)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': f'https://www.instagram.com/p/{shortcode}/',
        }
        
        yield scrapy.Request(
            url=url,
            headers=headers,
            cookies={'sessionid': self.sessionid},
            callback=self.parse_comments,
            meta={'shortcode': shortcode},
            dont_filter=True
        )
    
    def parse_comments(self, response):
        """Processa comentários."""
        shortcode = response.meta['shortcode']
        
        try:
            data = json.loads(response.text)
            edges = data.get('data', {}).get('shortcode_media', {}).get('edge_media_to_parent_comment', {}).get('edges', [])
            
            self.logger.info(f"✅ {len(edges)} comentários do post {shortcode}")
            
            for edge in edges:
                node = edge.get('node', {})
                
                yield InstagramCommentItem(
                    comment_id=node.get('id'),
                    post_shortcode=shortcode,
                    ownerUsername=node.get('owner', {}).get('username'),
                    text=node.get('text', ''),
                    created_at=datetime.fromtimestamp(node.get('created_at', 0)).isoformat(),
                    like_count=node.get('edge_liked_by', {}).get('count', 0),
                    candidato_id=self.username,
                    tier_used=1,
                    scraped_at=datetime.now().isoformat()
                )
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar comentários: {e}")
