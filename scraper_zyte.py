import httpx
import json
import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ScraperZyte")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class InstagramScraperZyte:
    def __init__(self, target_profile: str, max_posts: int = 5):
        self.target_profile = target_profile
        self.max_posts = max_posts
        self.zyte_key = os.getenv("ZYTE_API_KEY")
        self.zyte_api_url = "https://api.zyte.com/v1/extract"
        self.app_id = "936619743392459" # ID padrão do IG Web
        
        if not self.zyte_key:
            raise ValueError("❌ ZYTE_API_KEY não encontrada no ambiente.")

    async def _zyte_request(self, url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Faz uma requisição via Zyte API."""
        payload = {
            "url": url,
            "httpResponseBody": True,
        }
        if headers:
            # Zyte API v1 espera requestHeaders se quisermos passar headers customizados
            # Nota: Zyte pode sobrescrever alguns headers para garantir sucesso
            payload["customHttpRequestHeaders"] = [
                {"name": k, "value": v} for k, v in headers.items()
            ]

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.zyte_api_url,
                auth=(self.zyte_key, ""),
                json=payload
            )
            
            if response.status_code == 200:
                import base64
                res_data = response.json()
                body_b64 = res_data.get("httpResponseBody")
                if body_b64:
                    body_content = base64.b64decode(body_b64).decode('utf-8')
                    try:
                        return json.loads(body_content)
                    except json.JSONDecodeError:
                        logger.error(f"❌ Resposta não é JSON. Começo: {body_content[:200]}")
                        return {"raw_body": body_content}
            else:
                logger.error(f"❌ Erro Zyte ({response.status_code}): {response.text}")
                return {}

    async def fetch_recent_posts(self) -> List[Dict[str, Any]]:
        logger.info(f"🚀 [Zyte] Coletando perfil: {self.target_profile}")
        
        # 1. Busca Informações do Perfil e Posts
        profile_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={self.target_profile}"
        headers = {
            "X-IG-App-ID": self.app_id,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        
        data = await self._zyte_request(profile_url, headers)
        user_data = data.get("data", {}).get("user", {})
        
        if not user_data:
            logger.warning(f"⚠️ Resposta da API: {data}")
            logger.warning(f"⚠️ Não foi possível obter dados do perfil @{self.target_profile} via Zyte.")
            return []

        edges = user_data.get("edge_owner_to_timeline_media", {}).get("edges", [])
        detailed_posts = []
        
        for edge in edges[:self.max_posts]:
            node = edge.get("node", {})
            shortcode = node.get("shortcode")
            media_id = node.get("id")
            
            # Legenda
            caption = ""
            caption_edges = node.get("edge_media_to_caption", {}).get("edges", [])
            if caption_edges:
                caption = caption_edges[0].get("node", {}).get("text", "")

            post_item = {
                "shortcode": shortcode,
                "text": caption,
                "timestamp": node.get("taken_at_timestamp"),
                "comments": []
            }

            # 2. Busca Comentários do Post
            if media_id:
                logger.info(f"💬 [Zyte] Coletando comentários do post {shortcode}...")
                comments_url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
                comments_data = await self._zyte_request(comments_url, headers)
                
                raw_comments = comments_data.get("comments", [])
                for c in raw_comments[:10]: # Limite de 10 comentários por post
                    post_item["comments"].append({
                        "id": c.get("pk"),
                        "text": c.get("text"),
                        "ownerUsername": c.get("user", {}).get("username"),
                        "timestamp": c.get("created_at")
                    })
            
            detailed_posts.append(post_item)
            
        return detailed_posts

async def main():
    scraper = InstagramScraperZyte("cironogueira", max_posts=2)
    posts = await scraper.fetch_recent_posts()
    print(json.dumps(posts, indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
