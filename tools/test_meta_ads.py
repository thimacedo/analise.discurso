
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import os
import sys

# Adiciona a raiz do projeto ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.meta_ad_scraper import meta_ad_scraper

async def main():
    print("🚀 [TEST] Iniciando teste do Meta Ad Scraper...")
    # Testa com um alvo conhecido (ou genérico para ver se extrai cards)
    target = "lulaoficial" 
    print(f"📡 Testando extração para: @{target}")
    
    await meta_ad_scraper.scrape_ads_for_target(target)
    
    print("✅ [TEST] Teste concluído. Verifique os logs e o banco de dados.")

if __name__ == "__main__":
    asyncio.run(main())
