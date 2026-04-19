import base64
import os

class BrowserbaseProxyMiddleware:
    """
    Roteia todas as requisições através dos IPs residenciais do Browserbase.
    Isso evita bloqueios de IP (429/403) no Instagram.
    """
    def __init__(self, api_key, project_id):
        self.api_key = api_key
        self.project_id = project_id
        # Endpoint de proxy do Browserbase (ajustado para o padrão de mercado)
        self.proxy_url = "http://proxy.browserbase.com:8080"
        self.auth = base64.b64encode(f"{api_key}:{project_id}".encode()).decode()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            api_key=crawler.settings.get("BROWSERBASE_API_KEY"),
            project_id=crawler.settings.get("BROWSERBASE_PROJECT_ID")
        )

    def process_request(self, request, spider):
        # Apenas roteia se as chaves estiverem configuradas
        if self.api_key and self.project_id:
            request.meta["proxy"] = self.proxy_url
            request.headers["Proxy-Authorization"] = f"Basic {self.auth}"
            spider.logger.debug(f"🛡️ Roteando via Browserbase Proxy: {request.url}")
