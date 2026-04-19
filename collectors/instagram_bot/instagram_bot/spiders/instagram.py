import os
import json
import scrapy
from datetime import datetime
from instagram_bot.items import InstagramBotItem

class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["instagram.com"]
    
    # Perfil Monitor Fixo
    MONITOR_USERNAME = "monitoramento.discurso"
    MONITOR_ID = "69168962266"

    def __init__(self, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.session_id = os.environ.get("INSTAGRAM_SESSIONID")
        self.cookies = {"sessionid": self.session_id} if self.session_id else {}
        self.headers = {
            "X-IG-App-ID": "936619743392459",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def start_requests(self):
        if not self.session_id:
            self.logger.error("INSTAGRAM_SESSIONID não encontrada. Abortando.")
            return

        self.logger.info(f"[STEALTH] Iniciando coleta para {self.MONITOR_USERNAME}")
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={self.MONITOR_USERNAME}"
        yield scrapy.Request(
            url=url,
            cookies=self.cookies,
            headers=self.headers,
            callback=self.parse_monitor,
            errback=self.handle_monitor_error,
            dont_filter=True
        )

    def handle_monitor_error(self, failure):
        self.logger.warning(f"[STEALTH] web_profile_info falhou ({failure.value}). Tentando fallback direto para MONITOR_ID {self.MONITOR_ID}")
        following_url = f"https://www.instagram.com/api/v1/friendships/{self.MONITOR_ID}/following/"
        yield scrapy.Request(
            url=following_url,
            cookies=self.cookies,
            headers=self.headers,
            callback=self.parse_following,
            dont_filter=True
        )

    def parse_monitor(self, response):
        self.logger.info(f"[STEALTH] Resposta web_profile_info: {response.status}")
        if response.status == 429:
            self.logger.warning("[STEALTH] Rate Limit atingido no monitor. Acionando fallback direto.")
            # O errback nem sempre é chamado para 429 se o middleware de retry estiver ativo
            # Então forçamos o fallback aqui se necessário.
            following_url = f"https://www.instagram.com/api/v1/friendships/{self.MONITOR_ID}/following/"
            yield scrapy.Request(
                url=following_url,
                cookies=self.cookies,
                headers=self.headers,
                callback=self.parse_following,
                dont_filter=True
            )
            return

        try:
            data = json.loads(response.text)
            user_id = data["data"]["user"]["id"]
            self.logger.info(f"Monitor {self.MONITOR_USERNAME} identificado (ID: {user_id}). Buscando seguidos...")

            # Extrair Seguidos
            following_url = f"https://www.instagram.com/api/v1/friendships/{user_id}/following/"
            yield scrapy.Request(
                url=following_url,
                cookies=self.cookies,
                headers=self.headers,
                callback=self.parse_following
            )
        except Exception as e:
            self.logger.error(f"Falha ao processar monitor: {e}. Tentando fallback direto.")
            following_url = f"https://www.instagram.com/api/v1/friendships/{self.MONITOR_ID}/following/"
            yield scrapy.Request(
                url=following_url,
                cookies=self.cookies,
                headers=self.headers,
                callback=self.parse_following,
                dont_filter=True
            )

    def parse_following(self, response):
        self.logger.info(f"[STEALTH] Resposta Following List: {response.status}")
        try:
            data = json.loads(response.text)
            users = data.get('users', [])
            self.logger.info(f"[STEALTH] Encontrados {len(users)} seguidos.")
            
            for user in users:
                target_user_id = user.get('pk')
                target_username = user.get('username')
                full_name = user.get('full_name')

                yield InstagramBotItem(
                    item_type="profile",
                    user_id=str(target_user_id),
                    username=target_username,
                    full_name=full_name
                )

                # Para cada seguido, busca os 3 últimos posts
                feed_url = f"https://www.instagram.com/api/v1/feed/user/{target_user_id}/"
                self.logger.debug(f"[STEALTH] Solicitando feed de {target_username}")
                yield scrapy.Request(
                    url=feed_url,
                    cookies=self.cookies,
                    headers=self.headers,
                    callback=self.parse_feed,
                    meta={'username': target_username}
                )
        except Exception as e:
            self.logger.error(f"[STEALTH] Erro ao processar lista de seguidos: {e}")

    def parse_feed(self, response):
        self.logger.info(f"[STEALTH] Resposta Feed User ({response.meta['username']}): {response.status}")
        try:
            data = json.loads(response.text)
            items = data.get('items', [])
            owner_username = response.meta['username']

            for post_item in items[:3]:
                media_id = post_item.get('id')
                shortcode = post_item.get('code')
                
                yield InstagramBotItem(
                    item_type="post",
                    post_id=str(media_id),
                    shortcode=shortcode,
                    owner_username=owner_username,
                    text=post_item.get('caption', {}).get('text') if post_item.get('caption') else "",
                    timestamp=post_item.get('taken_at')
                )

                # Busca Comentários (Limite 100)
                comments_url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
                self.logger.debug(f"[STEALTH] Solicitando comentários do post {shortcode}")
                yield scrapy.Request(
                    url=comments_url,
                    cookies=self.cookies,
                    headers=self.headers,
                    callback=self.parse_comments,
                    meta={'post_shortcode': shortcode}
                )
        except Exception as e:
            self.logger.error(f"[STEALTH] Erro ao processar feed de {response.meta.get('username')}: {e}")

    def parse_comments(self, response):
        self.logger.info(f"[STEALTH] Resposta Comentários ({response.meta['post_shortcode']}): {response.status}")
        try:
            data = json.loads(response.text)
            comments = data.get('comments', [])
            post_shortcode = response.meta['post_shortcode']

            for comment in comments[:100]:
                yield InstagramBotItem(
                    item_type="comment",
                    comment_id=str(comment.get('pk')),
                    post_shortcode=post_shortcode,
                    owner_username=comment.get('user', {}).get('username'),
                    text=comment.get('text'),
                    timestamp=comment.get('created_at')
                )
        except Exception as e:
            self.logger.error(f"[STEALTH] Erro ao processar comentários: {e}")
