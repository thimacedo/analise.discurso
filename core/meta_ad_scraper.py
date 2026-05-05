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
                
                # Seletores robustos: Prioridade para data-testid, depois classes comuns
                cards = await page.query_selector_all('div[data-testid="ad_library_ad_card"], div.x1iyjqo2, div[data-ad-preview="message"]')
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
                            # Tenta persistir via db_client se disponível, senão apenas loga
                            if hasattr(db_client, 'persist_ad'):
                                await db_client.persist_ad(ad_data)
                                print(f"     ✅ Anúncio {ad_data['ad_id']} persistido.")
                            else:
                                print(f"     ✅ Anúncio {ad_data['ad_id']} extraído (DB offline).")
                    except Exception as e:
                        print(f"     ⚠️ Erro ao extrair card: {e}")

            except Exception as e:
                print(f"❌ [MetaAds] Erro ao acessar Ad Library: {e}")
            finally:
                await browser.close()

    async def _extract_card_data(self, card, candidato_id: str) -> Optional[Dict[str, Any]]:
        """Extrai dados de um card individual de anúncio com seletores mais granulares."""
        text = await card.inner_text()
        
        # ID do Anúncio (Fundamental)
        id_match = re.search(r'ID: (\d+)', text)
        if not id_match:
            # Tenta buscar em atributos se não achou no texto
            id_attr = await card.get_attribute("id")
            if id_attr and id_attr.isdigit():
                ad_id = id_attr
            else:
                return None
        else:
            ad_id = id_match.group(1)
        
        # Pagador (Funding Entity)
        pagador_match = re.search(r'(?:Pago por|Paid by|Patrocinado por|Sponsored by)\s+([^\n]+)', text, re.IGNORECASE)
        paid_by = pagador_match.group(1).strip() if pagador_match else "Privado/Não informado"
        
        # Spend Range (Valores) - Extração Numérica para o DB
        valor_match = re.findall(r'R\$\s*([\d\.]+)', text)
        v_min, v_max = 0.0, 0.0
        try:
            if len(valor_match) >= 2:
                v_min = float(valor_match[0].replace('.', '').replace(',', '.'))
                v_max = float(valor_match[1].replace('.', '').replace(',', '.'))
            elif len(valor_match) == 1:
                v_min = float(valor_match[0].replace('.', '').replace(',', '.'))
        except: pass

        # Alcance (Impressões)
        impressions_match = re.search(r'([\d\.]+)\s*-\s*([\d\.]+)\s*(?:impressões|impressions)', text)
        a_min, a_max = 0, 0
        if impressions_match:
            try:
                a_min = int(impressions_match.group(1).replace('.', ''))
                a_max = int(impressions_match.group(2).replace('.', ''))
            except: pass

        # Status do anúncio
        status = "active" if any(x in text for x in ["Ativo", "Active", "Em veiculação"]) else "inactive"

        # URL do anúncio
        ad_url = f"https://www.facebook.com/ads/library/?id={ad_id}"

        # Nome da Página
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        page_name = lines[0] if lines else "Página Oculta"

        # Creative Body (Corpo do texto)
        creative_body = ""
        for line in lines[1:10]:
            if len(line) > 30 and "ID:" not in line and "Pago por" not in line:
                creative_body = line
                break

        return {
            "ad_id": ad_id,
            "candidato_id": candidato_id,
            "page_name": page_name,
            "pagador": paid_by,
            "valor_min": v_min,
            "valor_max": v_max,
            "alcance_min": a_min,
            "alcance_max": a_max,
            "status": status,
            "ad_url": ad_url,
            "corpo_anuncio": creative_body,
            "processado_ia": False,
            "updated_at": datetime.now().isoformat()
        }

meta_ad_scraper = MetaAdScraper()
