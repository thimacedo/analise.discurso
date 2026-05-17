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

    async def _zyte_request(self, url: str, headers: Dict[str, str] = None, cookies: str = None, use_browser: bool = False) -> Dict[str, Any]:
        """Faz uma requisição via Zyte API."""
        payload = {
            "url": url,
        }
        
        custom_headers = []
        if headers:
            for k, v in headers.items():
                custom_headers.append({"name": k, "value": v})
        
        if cookies:
            custom_headers.append({"name": "Cookie", "value": cookies})

        if use_browser:
            payload["browserHtml"] = True
            payload["javascript"] = True
        else:
            payload["httpResponseBody"] = True
            if custom_headers:
                payload["customHttpRequestHeaders"] = custom_headers

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.zyte_api_url,
                auth=(self.zyte_key, ""),
                json=payload
            )
            
            if response.status_code == 200:
                res_data = response.json()
                
                if use_browser:
                    return {"browserHtml": res_data.get("browserHtml")}
                
                import base64
                body_b64 = res_data.get("httpResponseBody")
                if body_b64:
                    body_content = base64.b64decode(body_b64).decode('utf-8')
                    try:
                        if body_content.strip().startswith('{'):
                            return json.loads(body_content)
                        return {"raw_body": body_content}
                    except json.JSONDecodeError:
                        return {"raw_body": body_content}
            else:
                logger.error(f"❌ Erro Zyte ({response.status_code}): {response.text}")
                return {}

    def _extract_json_from_html(self, html: str) -> Dict[str, Any]:
        """Extrai o JSON do window._sharedData ou window.__additionalData do HTML do Instagram."""
        import re
        # Tenta __additionalData
        match = re.search(r'window\.__additionalData\["xdt_api__v1__users__web_profile_info"\s*\]\s*=\s*({.*?});', html, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except: pass
            
        # Tenta _sharedData
        match = re.search(r'window\._sharedData\s*=\s*({.*?});', html, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except: pass
            
        return {}

    def _extract_from_dom(self, html: str) -> List[Dict[str, Any]]:
        """Extrai posts via regex básicos se o JSON falhar."""
        import re
        posts = []
        
        # Encontra todos os hrefs que parecem posts ou reels
        # Formato: /username/p/CODE/ ou /p/CODE/
        links = re.findall(r'href="/(?:[^/]+/)?(p|reel)/([^/"]+)/"', html)
        
        seen_codes = set()
        for type_cmd, shortcode in links:
            if shortcode not in seen_codes:
                posts.append({
                    "shortcode": shortcode,
                    "text": f"[Extraído via DOM - {type_cmd}]", 
                    "timestamp": None,
                    "comments": []
                })
                seen_codes.add(shortcode)
                if len(posts) >= self.max_posts:
                    break
        return posts

    async def fetch_post_comments(self, post_url: str, external_cookies: Any = None) -> Dict[str, Any]:
        """Extrai comentários de uma URL de postagem específica."""
        logger.info(f"🔍 [Zyte] Coletando comentários da postagem: {post_url}")
        
        cookie_str = ""
        if isinstance(external_cookies, str):
            cookie_str = external_cookies
        elif isinstance(external_cookies, list):
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in external_cookies])

        # 1. Obter o HTML da página do post para encontrar o Media ID ou JSON embutido
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        
        res = await self._zyte_request(post_url, headers, cookie_str, use_browser=True)
        html = res.get("browserHtml", "")
        
        if not html:
            logger.error(f"❌ Falha ao carregar postagem: {post_url}")
            return {}

        # 2. Tenta extrair shortcode da URL
        import re
        shortcode_match = re.search(r'/(?:p|reel)/([^/?#&]+)', post_url)
        shortcode = shortcode_match.group(1) if shortcode_match else "unknown"

        # 3. Tenta encontrar o Media ID no HTML (necessário para a API de comentários)
        media_id_match = re.search(r'"media_id":"(\d+)"', html)
        media_id = media_id_match.group(1) if media_id_match else None
        
        comments = []
        caption = "[Extraído via Zyte]"

        if media_id:
            logger.info(f"💬 [Zyte] Media ID {media_id} encontrado. Chamando API de comentários...")
            comments_url = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
            api_headers = {
                "X-IG-App-ID": self.app_id,
                "User-Agent": headers["User-Agent"]
            }
            comments_data = await self._zyte_request(comments_url, api_headers, cookie_str)
            
            raw_comments = comments_data.get("comments", [])
            for c in raw_comments:
                comments.append({
                    "id": c.get("pk"),
                    "text": c.get("text"),
                    "ownerUsername": c.get("user", {}).get("username"),
                    "timestamp": c.get("created_at")
                })
        else:
            logger.warning("⚠️ Media ID não encontrado. Tentando extração de comentários via DOM...")
            # Fallback DOM para comentários (difícil sem scroll, mas capturamos o que houver)
            # Geralmente comentários estão em spans dentro de uls
            comment_matches = re.findall(r'<span>([^<]{5,200})</span>', html)
            for text in comment_matches[:20]:
                if len(text) > 10 and caption not in text:
                    comments.append({
                        "id": f"dom_{hash(text)}",
                        "text": text,
                        "ownerUsername": "unknown",
                        "timestamp": None
                    })

        return {
            "shortcode": shortcode,
            "text": caption,
            "comments": comments
        }

    async def fetch_recent_posts(self, external_cookies: Any = None) -> List[Dict[str, Any]]:
        logger.info(f"🚀 [Zyte] Coletando perfil: {self.target_profile}")
        
        cookie_str = ""
        if isinstance(external_cookies, str):
            cookie_str = external_cookies
        elif isinstance(external_cookies, list):
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in external_cookies])

        profile_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={self.target_profile}"
        headers = {
            "X-IG-App-ID": self.app_id,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        user_data = None
        
        # Tentativa 1: API JSON direta
        data = await self._zyte_request(profile_url, headers, cookie_str)
        user_data = data.get("data", {}).get("user", {})
        
        # Tentativa 2: Fallback para Browser Rendering
        if not user_data:
            logger.info(f"🔄 [Zyte] API JSON falhou. Tentando via Browser Rendering...")
            browser_url = f"https://www.instagram.com/{self.target_profile}/"
            browser_res = await self._zyte_request(browser_url, {"User-Agent": headers["User-Agent"]}, cookie_str, use_browser=True)
            
            html = browser_res.get("browserHtml", "")
            if html:
                extracted_data = self._extract_json_from_html(html)
                if "entry_data" in extracted_data:
                    user_data = extracted_data.get("entry_data", {}).get("ProfilePage", [{}])[0].get("graphql", {}).get("user", {})
                elif "data" in extracted_data:
                    user_data = extracted_data.get("data", {}).get("user", {})
                
                if not user_data:
                    logger.info("🔄 [Zyte] JSON não encontrado no HTML. Tentando extração via seletores CSS...")
                    dom_posts = self._extract_from_dom(html)
                    if dom_posts:
                        logger.info(f"✅ [Zyte] Extraídos {len(dom_posts)} posts via seletores CSS.")
                        return dom_posts

        if not user_data:
            logger.warning(f"❌ Não foi possível obter dados do perfil @{self.target_profile} por nenhum método Zyte.")
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
                comments_data = await self._zyte_request(comments_url, headers, cookie_str)
                
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
