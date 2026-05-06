import asyncio
import sys
import os

# Adiciona o diretório raiz ao sys.path para permitir imports do core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.meta_ad_service import meta_ad_service
from core.meta_ad_scraper import meta_ad_scraper
from core.config import settings

async def run_hybrid_collection(target_query: str):
    print(f"\n🚀 [Sentinela] Iniciando teste de coleta híbrida para: '{target_query}'")
    
    # 1. Tenta via API (Resiliência Refatorada no Passo 1)
    print("🔍 [Passo 1] Tentando coleta via Meta Ads API...")
    ads_api = await meta_ad_service.search_ads(target_query)
    
    if ads_api:
        print(f"✅ [API] Sucesso! {len(ads_api)} anúncios encontrados via API.")
        return ads_api
    
    print("⚠️ [API] Nenhum anúncio encontrado ou API indisponível (Token ausente).")
    
    # 2. Fallback para Scraper (Resiliência Refatorada no Passo 2)
    print(f"🕵️ [Passo 2] Iniciando Fallback: Scraper Headless para '{target_query}'...")
    try:
        # Nota: O scraper do MetaAdScraper persiste direto no banco por padrão
        # mas aqui vamos apenas rodar para validar a extração
        await meta_ad_scraper.scrape_ads_for_target(target_query)
        print("✅ [Scraper] Fluxo de scraper finalizado.")
    except Exception as e:
        print(f"❌ [Scraper] Falha crítica no fallback do scraper: {e}")

async def main():
    # Alvo de teste (pode ser um termo de busca ou @username)
    target = "Candidato Teste"
    
    # Verifica se temos token para decidir o que esperar
    if not settings.META_ACCESS_TOKEN:
        print("💡 [DICA] META_ACCESS_TOKEN não detectado no .env. O script deve ir direto para o Scraper.")
    
    await run_hybrid_collection(target)

if __name__ == "__main__":
    asyncio.run(main())
