import scrapy
import json
import os
from datetime import datetime

class InstagramSpider(scrapy.Spider):
    name = "instagram"
    
    def __init__(self, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.session_id = os.getenv("INSTAGRAM_SESSIONID")
        # App ID estático exigido pela API v1 do Instagram Web
        self.app_id = "936619743392459" 
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-IG-App-ID": self.app_id,
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": f"sessionid={self.session_id}"
        }
        
        # Carrega alvos de monitoramento
        try:
            # Tenta ler o arquivo de prioridade
            with open('E:/projetos/sentinela-democratica/data/priority_queue.json', 'r') as f:
                self.targets = json.load(f)
        except:
            # Fallback para alvos críticos se o arquivo falhar
            self.targets = ["lulaoficial", "flaviobolsonaro", "nikolasferreirainfo", "erikahiltonoficial"]

    def start_requests(self):
        for username in self.targets:
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
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
        username = response.meta['username']
        if response.status != 200:
            self.logger.error(f"❌ Falha no perfil {username} (Status {response.status})")
            return

        try:
            data = json.loads(response.text)
            user = data.get('data', {}).get('user', {})
            if not user: return

            # Envia perfil para o pipeline (candidatos)
            yield {
                'type': 'profile',
                'username': user['username'],
                'full_name': user['full_name'],
                'bio': user.get('biography', ''),
                'seguidores': user.get('edge_followed_by', {}).get('count', 0)
            }

            edges = user.get('edge_owner_to_timeline_media', {}).get('edges', [])
            for edge in edges[:5]: # Analisa os últimos 5 posts
                node = edge['node']
                shortcode = node['shortcode']
                media_id = node['id']
                
                # Ignoramos o item 'post' no pipeline v18.5 pois a tabela não existe
                # Mas disparamos a coleta de comentários
                comments_url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
                c_headers = self.headers.copy()
                c_headers["Referer"] = f"https://www.instagram.com/p/{shortcode}/"
                
                yield scrapy.Request(
                    comments_url, 
                    headers=c_headers, 
                    callback=self.parse_comments, 
                    meta={
                        'post_shortcode': shortcode,
                        'candidato_username': user['username']
                    }
                )
        except Exception as e:
            self.logger.error(f"Erro no parse de {username}: {e}")

    def parse_comments(self, response):
        if response.status != 200:
            self.logger.warning(f"⚠️ Comentários inacessíveis para {response.meta['post_shortcode']} (Status {response.status})")
            return

        try:
            # Se redirecionou para login, o conteúdo não será JSON
            if not response.text.strip().startswith('{'):
                self.logger.error(f"🚫 Bloqueio de Login detectado para post {response.meta['post_shortcode']}")
                return

            data = json.loads(response.text)
            comments = data.get('comments', [])
            for comment in comments[:50]:
                item = {
                    'type': 'comment',
                    'id': comment['pk'],
                    'text': comment.get('text', ''),
                    'owner_username': comment.get('user', {}).get('username', 'desconhecido'),
                    'timestamp': comment.get('created_at'),
                    'likes_count': comment.get('comment_like_count', 0),
                    'post_shortcode': response.meta['post_shortcode'],
                    'candidato_username': response.meta['candidato_username']
                }
                
                if not item['text'] or item['owner_username'] == 'desconhecido':
                    self.logger.warning(f"⚠️ Dados incompletos no comentário {item['id']} de {item['candidato_username']}")
                
                yield item
        except Exception as e:
            self.logger.error(f"Erro no parse de comentários: {e}")
