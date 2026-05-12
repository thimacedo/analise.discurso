
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import asyncio
import os
from core.instagram_headless import InstagramHeadlessScraper

async def test_headless():
    print("🚀 Testando InstagramHeadlessScraper...")
    scraper = InstagramHeadlessScraper()
    # Vamos tentar raspar apenas um perfil público conhecido para teste
    # Mas o run() carrega do banco. Vamos modificar o run ou criar um método de teste.
    # Olhando o código de instagram_headless.py, o run() chama _load_pending_targets.
    
    # Para teste rápido, vamos apenas instanciar e ver se o login passa (ou se os cookies funcionam)
    await scraper.run(limit=1)

if __name__ == "__main__":
    asyncio.run(test_headless())
