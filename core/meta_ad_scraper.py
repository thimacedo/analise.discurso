import os
import re
import asyncio
import json
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
            
            # Aplica stealth manualmente via script de inicialização
            page = await context.new_page()
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
            """)
            
            # Carrega cookies se existirem e não estiverem vazios
            if os.path.exists("cookies.txt") and os.path.getsize("cookies.txt") > 0:
                try:
                    with open("cookies.txt", "r") as f:
                        cookies = json.load(f)
                        await context.add_cookies(cookies)
                except json.JSONDecodeError:
                    print("⚠️ [DEBUG] cookies.txt está corrompido. Ignorando.")
            else:
                print("⚠️ [DEBUG] cookies.txt vazio ou inexistente. Raspando sem sessão.")
            
            try:
                # Acessa a página limpa
                await page.goto("https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=BR", wait_until="networkidle")
                
                # Digita na busca
                search_input = page.get_by_placeholder("Pesquisar por palavra-chave ou anunciante")
                await search_input.fill(username)
                await search_input.press("Enter")
                
                await asyncio.sleep(8) # Espera a busca processar
                
                # Seletor de "desespero": busca por qualquer div que contenha a estrutura de um card
                cards = await page.query_selector_all('div.x1iyjqo2, div[data-ad-preview="message"], div[class*="AdLibraryAdCard"]')
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
