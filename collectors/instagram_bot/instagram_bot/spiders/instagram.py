import json
import scrapy
from instagram_bot.items import InstagramProfileItem, InstagramPostItem, InstagramCommentItem

class InstagramSpider(scrapy.Spider):
    name = "instagram"
    allowed_domains = ["www.instagram.com"]
    
    MONITOR_USERNAME = "monitoramento.discurso"
    
    def start_requests(self):
        session_id = self.settings.get("INSTAGRAM_SESSIONID")
        if not session_id:
            self.logger.error("INSTAGRAM_SESSIONID não configurado.")
            return

        headers = {
            "Cookie": f"sessionid={session_id}",
            "X-IG-App-ID": "936619743392459",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin"
        }

        # 1. Busca o ID do perfil monitor
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={self.MONITOR_USERNAME}"
        yield scrapy.Request(url, headers=headers, callback=self.parse_monitor)

    def parse_monitor(self, response):
        try:
            data = json.loads(response.text)
            user_id = data["data"]["user"]["id"]
            self.logger.info(f"Perfil monitor encontrado. ID: {user_id}")
            
            session_id = self.settings.get("INSTAGRAM_SESSIONID")
            headers = {"Cookie": f"sessionid={session_id}", "X-IG-App-ID": "936619743392459"}

            # 2. Inicia paginação da lista de seguidos (API REST)
            url = f"https://www.instagram.com/api/v1/friendships/{user_id}/following/?count=200"
            yield scrapy.Request(url, headers=headers, callback=self.parse_followings)
        except Exception as e:
            self.logger.error(f"Erro ao analisar monitor: {e}")

    def parse_followings(self, response):
        try:
            data = json.loads(response.text)
            users = data.get("users", [])
            session_id = self.settings.get("INSTAGRAM_SESSIONID")
            headers = {"Cookie": f"sessionid={session_id}", "X-IG-App-ID": "936619743392459"}

            for user in users:
                u_id = user["pk"]
                username = user["username"]
                full_name = user.get("full_name", "")

                yield InstagramProfileItem(
                    user_id=str(u_id),
                    username=username,
                    full_name=full_name
                )

                # 3. Para cada seguido, busca os 3 últimos posts
                posts_url = f"https://www.instagram.com/api/v1/feed/user/{u_id}/?count=3"
                yield scrapy.Request(
                    posts_url, 
                    headers=headers, 
                    callback=self.parse_posts,
                    cb_kwargs={"owner_username": username}
                )

            next_max_id = data.get("next_max_id")
            if next_max_id:
                next_url = response.url.split("?")[0] + f"?count=200&max_id={next_max_id}"
                yield scrapy.Request(next_url, headers=headers, callback=self.parse_followings)
        except Exception as e:
            self.logger.error(f"Erro em parse_followings: {e}")

    def parse_posts(self, response, owner_username):
        try:
            data = json.loads(response.text)
            items = data.get("items", [])
            session_id = self.settings.get("INSTAGRAM_SESSIONID")
            headers = {"Cookie": f"sessionid={session_id}", "X-IG-App-ID": "936619743392459"}

            for item in items[:3]:
                post_id = str(item["id"])
                shortcode = item["code"]
                caption = item.get("caption", {})
                text = caption.get("text", "") if caption else ""
                timestamp = item.get("taken_at")

                yield InstagramPostItem(
                    post_id=post_id,
                    shortcode=shortcode,
                    owner_username=owner_username,
                    text=text,
                    timestamp=timestamp
                )

                # 4. Busca comentários do post
                comments_url = f"https://www.instagram.com/api/v1/media/{post_id}/comments/?can_support_threading=true&permalink_enabled=false"
                yield scrapy.Request(
                    comments_url,
                    headers=headers,
                    callback=self.parse_comments,
                    cb_kwargs={"shortcode": shortcode, "collected": 0}
                )
        except Exception as e:
            self.logger.error(f"Erro em parse_posts: {e}")

    def parse_comments(self, response, shortcode, collected):
        try:
            data = json.loads(response.text)
            if data.get("status") == "fail": return

            comments = data.get("comments", [])
            session_id = self.settings.get("INSTAGRAM_SESSIONID")
            headers = {"Cookie": f"sessionid={session_id}", "X-IG-App-ID": "936619743392459"}

            for comment in comments:
                if collected >= 100: break
                
                yield InstagramCommentItem(
                    comment_id=str(comment["pk"]),
                    post_shortcode=shortcode,
                    owner_username=comment["user"]["username"],
                    text=comment["text"],
                    timestamp=comment.get("created_at")
                )
                collected += 1

            has_more = data.get("has_more_comments", False)
            if has_more and collected < 100:
                next_max_id = data.get("next_max_id")
                next_url = response.url.split("?")[0] + f"?can_support_threading=true&permalink_enabled=false&max_id={next_max_id}"
                yield scrapy.Request(
                    next_url,
                    headers=headers,
                    callback=self.parse_comments,
                    cb_kwargs={"shortcode": shortcode, "collected": collected}
                )
        except Exception as e:
            self.logger.error(f"Erro em parse_comments: {e}")
