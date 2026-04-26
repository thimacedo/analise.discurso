import asyncio
import pyotp
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def run_test():
    async with async_playwright() as p:
        # Iniciar navegador VISÍVEL (headless=False)
        # slow_mo ajuda a acompanhar os cliques e preenchimentos
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        
        url = 'http://localhost:8000/admin'
        print(f'🚀 Acessando {url}...')
        
        try:
            await page.goto(url)
            print('✅ Página carregada.')

            # Gerar TOTP
            secret = os.getenv('SENTINELA_ADMIN_TOTP_SECRET')
            totp = pyotp.TOTP(secret.strip())
            code = totp.now()
            print(f'🔑 Código TOTP Gerado: {code}')
            
            # Preencher e Submeter
            await page.wait_for_selector('#totp-code')
            await page.fill('#totp-code', code)
            await page.click('button:has-text("Desbloquear Sistema")')
            print('🖱️ Login submetido...')

            # Aguardar carregamento do painel
            await page.wait_for_selector('#admin-screen:not(.hidden)', timeout=15000)
            print('✅ Painel Administrativo Desbloqueado!')

            # Aguardar a tabela de alvos
            await page.wait_for_selector('#targets-table tr')
            print('📊 Alvos carregados com sucesso do Supabase.')
            
            # Manter aberto por alguns segundos para visualização humana
            print('👀 Mantendo navegador aberto por 10 segundos para conferência...')
            await asyncio.sleep(10)

        except Exception as e:
            print(f'❌ ERRO: {str(e)}')
            await asyncio.sleep(5)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
