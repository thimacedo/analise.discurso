import scrapy
import json
import os
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class InstagramSpider(scrapy.Spider):
    name = "instagram"
    
    def __init__(self, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.session_id = os.getenv("INSTAGRAM_SESSIONID")
        self.app_id = "936619743392459" 
        
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.headers_supa = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
        ]
        self.instagram_proxy = os.getenv("INSTAGRAM_PROXY")
        self.instagram_proxy_list = os.getenv("INSTAGRAM_PROXY_LIST", "").split(";") if os.getenv("INSTAGRAM_PROXY_LIST") else []
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-IG-App-ID": self.app_id,
            "X-Requested-With": "XMLHttpRequest",
            "Cookie": f"sessionid={self.session_id}"
        }
        
        # Carrega alvos de monitoramento DINAMICAMENTE do Supabase
        self.targets = self._fetch_dynamic_targets()

    def _fetch_active_candidates(self, limit=15):
        """Identifica perfis com maior movimentação e que merecem monitoramento em tempo real."""
        try:
            url = f"{self.supabase_url}/rest/v1/candidatos?select=username,comentarios_totais_count,score_risco,seguidores&status_monitoramento=eq.ATIVO&order=score_risco.desc,comentarios_totais_count.desc,seguidores.desc&limit={limit}"
            resp = httpx.get(url, headers=self.headers_supa)
            if resp.status_code == 200:
                return [item['username'] for item in resp.json() if item.get('username')]
        except Exception as e:
            print(f"⚠️ [Scrapy] Erro ao buscar alvos de maior movimento: {e}")
        return []

    def _fetch_dynamic_targets(self):
        print("🕷️ [Scrapy] Buscando alvos na priority_queue local...")
        queue_path = 'E:/projetos/sentinela-democratica/data/priority_queue.json'
        try:
            if os.path.exists(queue_path):
                with open(queue_path, 'r') as f:
                    targets = json.load(f)
                    if targets:
                        print(f"🎯 [Scrapy] Alvos carregados do arquivo: {len(targets)} perfis.")
                        return targets
        except Exception as e:
            print(f"⚠️ [Scrapy] Erro ao ler priority_queue: {e}")

        print("🕷️ [Scrapy] Buscando fila dinâmica de perfis no Supabase...")
        try:
            url = f"{self.supabase_url}/rest/v1/candidatos?select=username&last_scraped_at=is.null&limit=15"
            resp = httpx.get(url, headers=self.headers_supa)
            if resp.status_code == 200:
                targets = [item['username'] for item in resp.json()]
                if targets:
                    print(f"🎯 [Scrapy] Alvos sem raspagem anterior: {len(targets)} perfis.")
                    return targets

            cutoff = (datetime.utcnow() - timedelta(hours=48)).isoformat()
            url = f"{self.supabase_url}/rest/v1/candidatos?select=username&last_scraped_at=lt.{cutoff}&limit=15&order=last_scraped_at.asc"
            resp = httpx.get(url, headers=self.headers_supa)
            if resp.status_code == 200:
                targets = [item['username'] for item in resp.json()]
                if targets:
                    print(f"⏳ [Scrapy] Perfis antigos sem raspagem recente: {len(targets)} perfis.")
                    return targets

            high_activity = self._fetch_active_candidates(limit=15)
            if high_activity:
                print(f"🚀 [Scrapy] Alvos de maior movimentação: {len(high_activity)} perfis.")
                return high_activity

            print("⚠️ [Scrapy] Usando alvos estáticos como fallback final.")
            return ["lulaoficial", "flaviobolsonaro", "nikolasferreirainfo", "erikahiltonoficial"]
        except Exception as e:
            print(f"⚠️ [Scrapy] Erro ao buscar fila dinâmica: {e}")
            return ["lulaoficial", "flaviobolsonaro"]

    def _build_request_headers(self, username: str) -> dict:
        headers = self.headers.copy()
        headers["User-Agent"] = self.user_agents[hash(username) % len(self.user_agents)]
        headers["Referer"] = f"https://www.instagram.com/{username}/"
        return headers

    def _select_proxy(self) -> str | None:
        if self.instagram_proxy_list:
            return self.instagram_proxy_list[hash(datetime.utcnow().timestamp()) % len(self.instagram_proxy_list)]
        return self.instagram_proxy or None

    def start_requests(self):
        for username in self.targets:
            url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
            headers = self._build_request_headers(username)
            proxy = self._select_proxy()
            meta = {'username': username}
            if proxy:
                meta['proxy'] = proxy
            
            yield scrapy.Request(
                url,
                headers=headers,
                callback=self.parse_profile,
                meta=meta,
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
                c_headers = self._build_request_headers(user['username'])
                c_headers["Referer"] = f"https://www.instagram.com/p/{shortcode}/"
                proxy = self._select_proxy()
                meta = {
                    'post_shortcode': shortcode,
                    'candidato_username': user['username']
                }
                if proxy:
                    meta['proxy'] = proxy
                
                yield scrapy.Request(
                    comments_url,
                    headers=c_headers,
                    callback=self.parse_comments,
                    meta=meta
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
