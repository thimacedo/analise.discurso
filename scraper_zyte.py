import httpx
import json
import os
import logging
import asyncio
import base64
from typing import List, Dict, Any
from dotenv import load_dotenv
from core.circuit_breaker import zyte_circuit_breaker

load_dotenv()

logger = logging.getLogger("ScraperZyte")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class InstagramScraperZyte:
    def __init__(self, target_profile: str, max_posts: int = 5):
        self.target_profile = target_profile
        self.max_posts = max_posts
        self.zyte_key = os.getenv("ZYTE_API_KEY")
        self.zyte_api_url = "https://api.zyte.com/v1/extract"
        self.app_id = "936619743392459"
        
        if not self.zyte_key:
            raise ValueError("❌ ZYTE_API_KEY não encontrada no ambiente.")

    async def _zyte_request(self, url: str, headers: Dict[str, str] = None, cookies: str = None, use_browser: bool = False) -> Dict[str, Any]:
        """
        Faz uma requisição via Zyte API com Circuit Breaker e retentativas para erro 503.
        """
        if not zyte_circuit_breaker.can_execute("zyte_api"):
            return {"error": "circuit_open", "status_code": 999}

        payload = {"url": url}
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

        max_retries = 3
        base_delay = 5  # segundos

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(self.zyte_api_url, auth=(self.zyte_key, ""), json=payload)
                
                # Erro 503: Serviço indisponível, tentar novamente com backoff
                if response.status_code == 503:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"⚠️ [Zyte] 503 Service Unavailable (tentativa {attempt + 1}/{max_retries}). Tentando novamente em {delay}s...")
                    await asyncio.sleep(delay)
                    continue # Próxima iteração do loop de retentativa

                # Sucesso ou erro definitivo
                zyte_circuit_breaker.record_success("zyte_api")
                
                if response.status_code != 200:
                    logger.error(f"❌ Erro Zyte ({response.status_code}): {response.text[:200]}")
                    zyte_circuit_breaker.record_failure("zyte_api", response.status_code)
                    return {"error": "api_error", "status_code": response.status_code}
                
                res_data = response.json()
                target_status = res_data.get("statusCode", 200)
                if target_status == 404:
                    logger.error(f"⚠️ [Username Inválido] Perfil não encontrado (404): {url}")
                    return {"error": "not_found", "statusCode": 404}
                
                if use_browser:
                    return {"browserHtml": res_data.get("browserHtml"), "statusCode": target_status}
                
                body_b64 = res_data.get("httpResponseBody")
                if body_b64:
                    body_content = base64.b64decode(body_b64).decode('utf-8')
                    if body_content.strip().startswith('{'):
                        return json.loads(body_content)
                    return {"raw_body": body_content}
                
                return {} # Resposta 200 OK mas vazia

            except httpx.RequestError as e:
                logger.error(f"🔌 [Zyte] Erro de conexão/rede: {e}")
                # Não registra falha no CB por erro de rede local, mas quebra o loop
                return {"error": "connection_error"}
        
        # Se todas as retentativas falharem (apenas para 503)
        logger.error("❌ [Zyte] Falha definitiva após múltiplas tentativas (503).")
        zyte_circuit_breaker.record_failure("zyte_api", 503)
        return {"error": "service_unavailable", "status_code": 503}


    def _extract_json_from_html(self, html: str) -> Dict[str, Any]:
        """Extrai o JSON do window._sharedData ou window.__additionalData do HTML do Instagram."""
        import re
        if not html: return {}
        # Tenta __additionalData
        match = re.search(r'window\.__additionalData\["xdt_api__v1__users__web_profile_info"\s*\]\s*=\s*({.*?});', html, re.DOTALL)
        if match:
            try: return json.loads(match.group(1))
            except: pass
            
        # Tenta _sharedData
        match = re.search(r'window\._sharedData\s*=\s*({.*?});', html, re.DOTALL)
        if match:
            try: return json.loads(match.group(1))
            except: pass
            
        return {}

    def _extract_from_dom(self, html: str) -> List[Dict[str, Any]]:
        """Extrai posts via regex básicos se o JSON falhar."""
        import re
        if not html: return []
        posts = []
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

    async def fetch_recent_posts(self, external_cookies: Any = None) -> List[Dict[str, Any]]:
        """
        Orquestra a coleta de posts de um perfil, com múltiplos fallbacks.
        Retorna uma lista de posts ou uma lista vazia em caso de falha definitiva.
        """
        logger.info(f"🚀 [Zyte] Coletando perfil: {self.target_profile}")
        
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in external_cookies]) if isinstance(external_cookies, list) else external_cookies or ""

        profile_url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={self.target_profile}"
        headers = {
            "X-IG-App-ID": self.app_id,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        
        # Tentativa 1: API JSON direta
        data = await self._zyte_request(profile_url, headers, cookie_str)
        user_data = data.get("data", {}).get("user")
        
        # Tentativa 2: Fallback para Browser Rendering se a API falhar
        html_content_for_debug = ""
        if not user_data:
            logger.info("🔄 [Zyte] API JSON falhou. Tentando via Browser Rendering...")
            browser_url = f"https://www.instagram.com/{self.target_profile}/"
            browser_res = await self._zyte_request(browser_url, {"User-Agent": headers["User-Agent"]}, cookie_str, use_browser=True)
            
            html = browser_res.get("browserHtml", "")
            html_content_for_debug = html # Guarda para depuração
            
            if html:
                extracted_data = self._extract_json_from_html(html)
                user_data = (extracted_data.get("data", {}).get("user") or 
                            extracted_data.get("entry_data", {}).get("ProfilePage", [{}])[0].get("graphql", {}).get("user"))
                
                # Tentativa 3: Se JSON no HTML falhar, tenta extrair posts direto do DOM
                if not user_data:
                    logger.info("🔄 [Zyte] JSON não encontrado no HTML. Tentando extração via seletores CSS...")
                    dom_posts = self._extract_from_dom(html)
                    if dom_posts:
                        logger.info(f"✅ [Zyte] Extraídos {len(dom_posts)} posts via seletores CSS.")
                        return dom_posts

        if not user_data:
            logger.warning(f"❌ Não foi possível obter dados do perfil @{self.target_profile} por nenhum método Zyte.")
            # Salva o HTML para análise da falha
            if html_content_for_debug:
                with open(f"zyte_debug_response_{self.target_profile}.html", "w", encoding="utf-8") as f:
                    f.write(html_content_for_debug)
                logger.info(f"🐛 HTML de depuração salvo em 'zyte_debug_response_{self.target_profile}.html'")
            return []

        # Processamento dos dados obtidos (seja da API ou do JSON embutido)
        edges = user_data.get("edge_owner_to_timeline_media", {}).get("edges", [])
        # ... (Restante da lógica para processar os posts e comentários, se necessário) ...
        # Por simplicidade, vamos retornar os dados brutos dos posts aqui
        posts_data = []
        for edge in edges[:self.max_posts]:
             node = edge.get("node", {})
             posts_data.append({
                 "shortcode": node.get("shortcode"),
                 "text": node.get("edge_media_to_caption", {}).get("edges", [{}])[0].get("node", {}).get("text", ""),
                 "timestamp": node.get("taken_at_timestamp")
             })
        return posts_data

# ... (código de fetch_post_comments, main, etc., pode ser mantido ou adaptado)
async def main():
    # Exemplo de uso
    scraper = InstagramScraperZyte("rafaelfontelesoficial", max_posts=3)
    posts = await scraper.fetch_recent_posts()
    print(json.dumps(posts, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
