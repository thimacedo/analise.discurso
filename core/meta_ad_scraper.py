import os
import re
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, Page
from core.db import db_client
from core.config import settings

class MetaAdScraper:
    def __init__(self):
        self.headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
        self.base_url = "https://www.facebook.com/ads/library/"

    async def scrape_ads_for_target(self, username: str):
        """Scrape ads from Meta Ad Library for a specific target."""
        print(f"🔍 [MetaAds] Buscando anúncios para @{username}...")
        
        search_url = f"{self.base_url}?active_status=all&ad_type=all&country=BR&q={username}&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&media_type=all"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                locale="pt-BR",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            )
            
            # Aplica stealth
            from playwright_stealth import stealth_async
            page = await context.new_page()
            await stealth_async(page)
            
            # Carrega cookies se existirem
            if os.path.exists("cookies.txt"):
                with open("cookies.txt", "r") as f:
                    cookies = json.load(f)
                    await context.add_cookies(cookies)
            
            try:
                await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(5) # Aguarda renderização dos cards
                
                # Scroll para carregar mais anúncios
                await page.mouse.wheel(0, 1000)
                await asyncio.sleep(2)

                # Tentativa de seletor mais robusto, buscando por containers de cards de anúncio
                cards = await page.query_selector_all('div[data-testid="ad-library-ad-card"], div.x1y1ht1m')
                print(f"     📊 {len(cards)} cards de anúncios detectados visualmente.")

                if len(cards) == 0:
                    html_content = await page.content()
                    with open("debug_meta_ads.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    await page.screenshot(path="debug_meta_ads.png")
                    print("📸 [DEBUG] Nenhum anúncio encontrado. HTML e Screenshot salvos.")

                for card in cards:
                    try:
                        ad_data = await self._extract_card_data(card, username)
                        if ad_data:
                            await db_client.persist_ad(ad_data)
                            print(f"     ✅ Anúncio {ad_data['ad_id']} persistido.")
                    except Exception as e:
                        print(f"     ⚠️ Erro ao extrair card: {e}")

            except Exception as e:
                print(f"❌ [MetaAds] Erro ao acessar Ad Library: {e}")
            finally:
                await browser.close()

    async def _extract_card_data(self, card, candidato_id: str) -> Optional[Dict[str, Any]]:
        """Extrai dados de um card individual de anúncio."""
        text = await card.inner_text()
        
        # Procura pelo ID do anúncio
        id_match = re.search(r'ID: (\d+)', text)
        if not id_match:
            return None
        
        ad_id = id_match.group(1)
        
        # Procura por "Pago por" ou "Paid by"
        pagador_match = re.search(r'(?:Pago por|Paid by)\s+([^\n]+)', text)
        pagador = pagador_match.group(1) if pagador_match else "Desconhecido"
        
        # Procura por valores (ex: R$ 100 - R$ 499)
        valor_match = re.search(r'R\$\s*([\d\.]+)\s*-\s*R\$\s*([\d\.]+)', text)
        v_min, v_max = 0, 0
        if valor_match:
            v_min = float(valor_match.group(1).replace('.', '').replace(',', '.'))
            v_max = float(valor_match.group(2).replace('.', '').replace(',', '.'))

        # Status
        status = "active" if "Ativo" in text or "Active" in text else "inactive"

        return {
            "ad_id": ad_id,
            "candidato_id": candidato_id,
            "pagador": pagador,
            "valor_min": v_min,
            "valor_max": v_max,
            "status": status,
            "updated_at": datetime.now().isoformat()
        }

meta_ad_scraper = MetaAdScraper()
