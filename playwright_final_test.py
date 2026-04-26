import asyncio
import pyotp
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def run_test():
    async with async_playwright() as p:
        # 1. Iniciar navegador
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # URL da rota administrativa no servidor local
        url = 'http://localhost:8000/admin'
        print(f'🚀 Acessando {url}...')
        
        try:
            await page.goto(url, wait_until='networkidle')
            print('✅ Página carregada.')

            # 2. Gerar TOTP via Secret
            secret = os.getenv('SENTINELA_ADMIN_TOTP_SECRET')
            totp = pyotp.TOTP(secret.strip())
            code = totp.now()
            print(f'🔑 Código TOTP Gerado: {code}')
            
            # 3. Preencher o campo e clicar no botão
            # Verificamos se o seletor está disponível
            await page.wait_for_selector('#totp-code', timeout=5000)
            await page.fill('#totp-code', code)
            await page.click('button:has-text("Desbloquear Sistema")')
            print('🖱️ Botão clicado. Aguardando autenticação...')

            # 4. Validar se o painel administrativo foi exibido
            # O ID #admin-screen deve se tornar visível (remover classe hidden)
            await page.wait_for_selector('#admin-screen:not(.hidden)', timeout=10000)
            print('✅ LOGIN BEM-SUCEDIDO: Painel Administrativo Visível.')

            # 5. Validar carregamento de dados (tabela de alvos)
            await page.wait_for_selector('#targets-table tr', timeout=10000)
            rows = await page.query_selector_all('#targets-table tr')
            print(f'📊 TOTAL DE ALVOS CARREGADOS NA TABELA: {len(rows)}')
            
            # 6. Validar o botão de Baixar Modelo (apenas presença e URL)
            download_btn = await page.query_selector('button:has-text("Baixar Modelo")')
            if download_btn:
                print('✅ Botão "Baixar Modelo" verificado.')

        except Exception as e:
            print(f'❌ ERRO DURANTE O TESTE: {str(e)}')
            # Tirar print se possível (embora em modo headless/CLI não vejamos, ajuda no debug interno)
            await page.screenshot(path='test_error.png')
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
