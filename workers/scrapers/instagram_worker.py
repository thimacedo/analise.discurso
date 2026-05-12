# workers/scrapers/instagram_worker.py
import sys
import asyncio
import logging
import os
import random
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from workers.core.base_worker import BaseWorker
from core.db import save_alerts # NOSSO NOVO MÓDULO DE BANCO

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

load_dotenv()

# ==========================================
# MOTOR DE CLASSIFICAÇÃO PASA v16.4 (Simulado)
# Em produção, isso será substituído pela chamada à API do Gemini/LLM
# ==========================================
def classify_pasa(text: str) -> tuple:
    """Analisa o texto e retorna (category, is_critical) baseado no PASA."""
    if not text:
        return "NEUTRO", False
        
    text_lower = text.lower()
    
    # 1. Scanner de Ameaça (Crítico)
    if any(w in text_lower for w in ["tiro", "paredão", "matar", "morte"]):
        return "AMEACA", True
        
    # 2. Rigor Criminal
    if any(w in text_lower for w in ["ladrão", "corrupto", "traficante", "roubo"]):
        return "RIGOR_CRIMINAL", True
        
    # 3. Violência de Gênero
    if any(w in text_lower for w in ["vaca", "puta", "louca", "mulher feia"]):
        return "VIOLENCIA_GENERO", True
        
    # 4. Ódio Identitário / Regionalismo
    if any(w in text_lower for w in ["baiano preguiçoso", "nordestino", "xenofobia"]):
        return "ODIO_IDENTITARIO", True
        
    # 5. Ataque Institucional
    if any(w in text_lower for w in ["ditadura da toga", "stf ladrão", "fraude nas urnas"]):
        return "ATAQUE_INSTITUCIONAL", True
        
    # 6. Insulto Ad Hominem
    if any(w in text_lower for w in ["verme", "rato", "lixo", "escória"]):
        return "INSULTO_AD_HOMINEM", False

    # Se não cair em nada, é Neutro (Apoio agressivo, crítica política legítima, etc.)
    return "NEUTRO", False


class InstagramWorker(BaseWorker):
    """
    Worker oficial de raspagem do Instagram via Playwright Stealth.
    """
    def __init__(self, target_profile: str, max_posts: int = 5):
        super().__init__(name=f"InstagramWorker-{target_profile}")
        self.target_profile = target_profile
        self.profile_url = f"https://www.instagram.com/{target_profile}/"
        self.max_posts = max_posts 
        
        self.session_id = os.getenv("INSTAGRAM_SESSIONID")
        self.ds_user_id = os.getenv("INSTAGRAM_DS_USER_ID")
        self.csrf_token = os.getenv("INSTAGRAM_CSRFTOKEN")

        if not all([self.session_id, self.ds_user_id, self.csrf_token]):
            raise ValueError("❌ Variáveis de sessão do Instagram ausentes no .env")

    async def _inject_cookies(self, context):
        await context.add_cookies([
            {"name": "sessionid", "value": self.session_id, "domain": ".instagram.com", "path": "/", "httpOnly": True, "secure": True, "sameSite": "Lax"},
            {"name": "ds_user_id", "value": self.ds_user_id, "domain": ".instagram.com", "path": "/", "secure": True},
            {"name": "csrftoken", "value": self.csrf_token, "domain": ".instagram.com", "path": "/", "secure": True}
        ])

    async def _run(self, *args, **kwargs):
        self.logger.info(f"🚀 Iniciando Playwright Stealth para: {self.target_profile}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled', '--no-sandbox'])
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36", viewport={'width': 1920, 'height': 1080}, locale='pt-BR')
            
            await self._inject_cookies(context)
            page = await context.new_page()
            
            await page.add_init_script("""Object.defineProperty(navigator, 'webdriver', { get: () => undefined });""")
            
            try:
                await page.goto(self.profile_url, wait_until="domcontentloaded", timeout=30000)
                if "login" in page.url: raise Exception("Sessão do Instagram Inválida/Bloqueada")

                try: await page.click('button:has-text("Agora não"), button:has-text("Not Now")', timeout=2000)
                except: pass

                selector = 'a[href*="/p/"], a[href*="/reel/"]'
                await page.wait_for_selector(selector, timeout=15000)
                
                detailed_posts = []
                elements = await page.query_selector_all(selector)
                safe_limit = min(self.max_posts, 15, len(elements))
                
                for index, element in enumerate(elements[:safe_limit]):
                    try:
                        href = await element.get_attribute('href')
                        shortcode = href.strip('/').split('/')[-1]
                        
                        await element.click()
                        await page.wait_for_selector('div[role="dialog"]', timeout=10000)
                        await asyncio.sleep(random.uniform(1.5, 4.5)) 
                        
                        dialog_element = await page.query_selector('div[role="dialog"]')
                        if dialog_element:
                            time_element = await dialog_element.query_selector('time')
                            date_str = await time_element.get_attribute('datetime') if time_element else "Unknown"
                            
                            caption = ""
                            h1 = await dialog_element.query_selector('h1')
                            if h1: caption = await h1.inner_text()
                            else:
                                span = await dialog_element.query_selector('div[role="button"] span')
                                if span: caption = await span.inner_text()

                            # ==========================================
                            # A MAGIA ACONTECE AQUI: CLASSIFICAÇÃO E SALVAMENTO
                            # ==========================================
                            category, is_critical = classify_pasa(caption)

                            post_data = {
                                "id": shortcode, 
                                "shortcode": shortcode,
                                "text": caption.strip(),
                                "timestamp": date_str,
                                "profile": self.target_profile,
                                "target_profile": self.target_profile, # Campo que o Frontend espera
                                "category": category, # PASA classification
                                "is_critical": is_critical, # PASA severity
                                "source": "IG",
                                "target_avatar_url": "./assets/sentinela_small.webp"
                            }
                            detailed_posts.append(post_data)
                            self.logger.info(f"🔍 [{index+1}/{safe_limit}] {shortcode} -> Classificação: {category}")
                        
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(random.uniform(1.0, 3.0))

                    except Exception as e:
                        self.logger.warning(f"⚠️ Falha ao extrair post do modal: {e}")
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(2)
                
                # SALVA TODOS OS POSTS EXTRAÍDOS DE UMA VEZ NO SUPABASE
                if detailed_posts:
                    self.logger.info(f"💾 Salvando {len(detailed_posts)} alertas no Supabase...")
                    success = save_alerts(detailed_posts)
                    if success:
                        self.logger.info("✅ Sincronização com o banco concluída com sucesso!")
                    else:
                        self.logger.error("❌ Falha ao sincronizar com o banco.")

                return detailed_posts

            except Exception as e:
                self.logger.error(f"❌ Erro geral na raspagem: {e}")
                raise
            finally:
                await browser.close()

    def handle_failure(self, exception: Exception):
        self.logger.error(f"🚨 ALERTA DE FALHA NO WORKER {self.name}: {str(exception)}")

# Bloco de teste isolado
async def main():
    # Teste com um perfil real que tenha textos políticos ou agressivos para o PASA pegar
    worker = InstagramWorker("instagram", max_posts=3) 
    dados = await worker.execute()
    for d in dados: 
        print(f"ID: {d.get('id')} | PASA: {d.get('category')} | Texto: {d.get('text')[:50]}...")

if __name__ == "__main__":
    asyncio.run(main())
