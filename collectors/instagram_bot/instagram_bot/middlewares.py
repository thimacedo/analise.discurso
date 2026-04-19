import base64
import os

class ApifyProxyMiddleware:
    """
    Roteia todas as requisições através dos IPs residenciais do Apify.
    Solução estável e já validada no ambiente local.
    """
    def __init__(self, proxy_password):
        self.proxy_password = proxy_password
        # Endpoint de proxy do Apify
        self.proxy_url = "http://proxy.apify.com:8000"
        # O usuário do proxy apify é 'groups-RESIDENTIAL' para IPs residenciais
        self.auth = base64.b64encode(f"groups-RESIDENTIAL:{proxy_password}".encode()).decode()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxy_password=crawler.settings.get("APIFY_API_TOKEN")
        )

    def process_request(self, request, spider):
        if self.proxy_password:
            request.meta["proxy"] = self.proxy_url
            request.headers["Proxy-Authorization"] = f"Basic {self.auth}"
            spider.logger.debug(f"🛡️ Roteando via Apify Residential Proxy: {request.url}")
