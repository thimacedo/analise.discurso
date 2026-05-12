
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import re
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright
from core.supabase_service import get_supabase_client
from core.config import settings
from core.base_scraper import SentinelaScraper
from processing.monetization_engine import MonetizationEngine
from core.firebase_alerter import send_alert_summary

class MetaAdScraper(SentinelaScraper):
    def __init__(self):
        super().__init__("MetaAdScraper")
        self.headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"
        self.base_url = "https://www.facebook.com/ads/library/"
        self.monetization_engine = MonetizationEngine()
        self.db = get_supabase_client()

    def login(self):
        self.logger.info("Meta Ad Library não requer login explícito.")
        return True

    def scrape(self, username: str):
        asyncio.run(self.scrape_ads_for_target(username))

    async def scrape_ads_for_target(self, username: str):
        self.logger.info(f"Buscando anúncios para @{username}...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                locale="pt-BR",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
            """)
            
            try:
                await page.goto("https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=BR", wait_until="networkidle")
                search_input = page.get_by_placeholder("Pesquisar por palavra-chave ou anunciante")
                await search_input.fill(username)
                await search_input.press("Enter")
                
                await asyncio.sleep(8)
                
                cards = await page.query_selector_all('div[data-testid="ad_library_ad_card"], div.x1iyjqo2, div[data-ad-preview="message"]')
                self.logger.info(f"{len(cards)} cards detectados.")

                for card in cards:
                    try:
                        ad_data = await self._extract_card_data(card, username)
                        if ad_data:
                            if hasattr(self.db, 'persist_ad'):
                                await self.db.persist_ad(ad_data)
                                self.logger.info(f"Anúncio {ad_data['ad_id']} persistido.")
                                
                                # Lógica de alerta de monetização
                                if ad_data.get('risco_monetizacao') == 'High':
                                    send_alert_summary(f"ALERTA: Alta atividade de monetização para @{username}. Ad ID: {ad_data['ad_id']}")
                                    self.logger.warning(f"Alerta disparado para anúncio de risco: {ad_data['ad_id']}")

                    except Exception as e:
                        self.logger.warning(f"Erro ao extrair card: {e}")

            except Exception as e:
                self.logger.error(f"Erro ao acessar Ad Library: {e}")
            finally:
                await browser.close()

    async def _extract_card_data(self, card, candidato_id: str) -> Optional[Dict[str, Any]]:
        text = await card.inner_text()
        id_match = re.search(r'ID: (\d+)', text)
        ad_id = id_match.group(1) if id_match else (await card.get_attribute("id") or "0")
        
        pagador_match = re.search(r'(?:Pago por|Paid by|Patrocinado por|Sponsored by)\s+([^\n]+)', text, re.IGNORECASE)
        paid_by = pagador_match.group(1).strip() if pagador_match else "Privado/Não informado"
        
        finance_data = self.monetization_engine.extract_monetization_data({
            'ad_id': ad_id,
            'pagador': paid_by,
            'valor_min': 0.0,
            'valor_max': 0.0
        })

        return {
            "ad_id": ad_id,
            "candidato_id": candidato_id,
            "pagador": paid_by,
            "valor_min": finance_data.get('valor_estimado', 0.0),
            "risco_monetizacao": finance_data.get('risco_monetizacao', 'Low'),
            "updated_at": datetime.now().isoformat()
        }

if __name__ == "__main__":
    scraper = MetaAdScraper()
    scraper.scrape("exemplo_perfil")

meta_ad_scraper = MetaAdScraper()