# workers/scrapers/instagram_worker.py
import sys
import asyncio
import logging
import os
import random
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from workers.core.base_worker import BaseWorker
from core.supabase_service import save_alerts # NOSSO NOVO MÓDULO DE BANCO

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
        """Método principal exigido pelo BaseWorker. Executa a rotina de raspagem."""
        self.logger.info(f"🚀 Iniciando Playwright Stealth para: {self.target_profile}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True, 
                args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36", 
                viewport={'width': 1920, 'height': 1080}, 
                locale='pt-BR'
            )
            await self._inject_cookies(context)
            page = await context.new_page()

            # Stealth Patch
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['pt-BR', 'pt', 'en-US', 'en'] });
            """)

            try:
                # 1. Acessa o Perfil
                await page.goto(self.profile_url, wait_until="domcontentloaded", timeout=30000)

                # Aceitar Cookies (Obrigatório no Brasil/Europa, bloqueia o grid se não aceitar)
                try: 
                    await page.click('button:has-text("Aceitar"), button:has-text("Accept All"), button:has-text("Allow all cookies")', timeout=3000)
                    self.logger.info("🍪 Cookies aceitos.")
                    await asyncio.sleep(1)
                except: pass

                # Fecha pop-ups de notificação
                try: 
                    await page.click('button:has-text("Agora não"), button:has-text("Not Now")', timeout=2000)
                except: pass

                # 2. Scroll leve e pega apenas os 3 primeiros posts
                await page.evaluate("window.scrollTo(0, 300)") # Scroll mínimo
                await asyncio.sleep(2)

                selector = 'a[href*="/p/"], a[href*="/reel/"]'
                # Espera só o PRIMEIRO post aparecer
                try: 
                    await page.wait_for_selector(selector, timeout=15000, state="visible")
                except:
                    self.logger.error(f"❌ Nenhum post carregou para {self.target_profile}. Tirando print...")
                    await page.screenshot(path=f"erro_grid_{self.target_profile}.png")
                    raise Exception(f"Timeout ao aguardar grid de posts para {self.target_profile}")

                elements = await page.query_selector_all(selector)
                # FORÇA O LIMITE EM 3 POSTS
                elements = elements[:3]
                self.logger.info(f"✅ Encontrados {len(elements)} posts. Iniciando extração profunda de comentários...")

                # 3. Extração via Modal
                detailed_posts = []
                for index, element in enumerate(elements):
                    try:
                        href = await element.get_attribute('href')
                        shortcode = href.strip('/').split('/')[-1]
                        await element.click()
                        await page.wait_for_selector('div[role="dialog"]', timeout=10000)
                        await asyncio.sleep(random.uniform(2.0, 4.0))
                        
                        dialog_element = await page.query_selector('div[role="dialog"]')
                        if dialog_element:
                            # Extrai Data
                            time_element = await dialog_element.query_selector('time')
                            date_str = await time_element.get_attribute('datetime') if time_element else "Unknown"
                            
                            # Extrai Legenda (Caption)
                            caption = ""
                            h1 = await dialog_element.query_selector('h1')
                            if h1: caption = await h1.inner_text()
                            
                            # ==========================================
                            # NOVIDADE: EXTRAÇÃO DE COMENTÁRIOS
                            # ==========================================
                            # Scroll dentro do modal para carregar os comentários
                            await dialog_element.evaluate('el => el.scrollTop = el.scrollHeight')
                            await asyncio.sleep(2)
                            
                            comments_text = []
                            # Pega os textos dos comentários (geralmente estão em spans dentro de LIs)
                            comment_elements = await dialog_element.query_selector_all('ul ul li')
                            for c_el in comment_elements[:20]: # Limita a 20 comentários por post
                                c_text = await c_el.inner_text()
                                if c_text: comments_text.append(c_text.replace('\n', ' '))
                                
                            # Junta a legenda com os comentários para o PASA analisar tudo junto
                            full_text = caption.strip()
                            if comments_text:
                                full_text += " | COMENTÁRIOS: " + " // ".join(comments_text)
                                
                            # Classifica e salva
                            category, is_critical = classify_pasa(full_text)
                            post_data = {
                                "id": shortcode, 
                                "text": full_text.strip(), # Texto completo (Legenda + Comentários)
                                "timestamp": date_str,
                                "target_profile": self.target_profile,
                                "category": category,
                                "is_critical": is_critical,
                                "source": "IG",
                                "target_avatar_url": "./assets/sentinela_small.webp"
                            }
                            detailed_posts.append(post_data)
                            self.logger.info(f"🔍 [{index+1}/3] {shortcode} -> PASA: {category} (Comentários: {len(comments_text)})")
                            
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(random.uniform(2.0, 4.0))

                    except Exception as e:
                        self.logger.warning(f"⚠️ Falha ao extrair post do modal: {e}")
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(2)

                # Salva no Supabase
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
