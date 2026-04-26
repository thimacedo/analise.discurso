import asyncio
from playwright.async_api import async_playwright

async def run_ui_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = 'http://127.0.0.1:8000/'
        print(f'🚀 Acessando {url}...')
        
        try:
            # Capturar logs de erro do console
            errors = []
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
            
            await page.goto(url)
            await page.wait_for_timeout(3000)
            
            # Tentar navegar para o Dossiê
            print('🖱️ Clicando em Dossiê de Alvos...')
            await page.click('#nav-dossie')
            await page.wait_for_timeout(2000)
            
            # Verificar se a view do dossiê está visível
            is_visible = await page.is_visible('#view-dossie:not(.hidden)')
            print(f'👀 View Dossiê Visível: {is_visible}')
            
            # Verificar se a grade foi populada
            has_grid = await page.is_visible('#dossie-grid div')
            print(f'📊 Grade do Dossiê Populada: {has_grid}')

            if errors:
                print('⚠️ ERROS DE CONSOLE:')
                for err in errors: print(f'   - {err}')
            
            if not is_visible or not has_grid:
                print('❌ FALHA NA RENDERIZAÇÃO DO DOSSIÊ.')
            else:
                print('✅ DOSSIÊ FUNCIONANDO LOCALMENTE.')

            # Tentar navegar para Geopolítica
            print('🖱️ Clicando em Geopolítica UF...')
            await page.click('#nav-map')
            await page.wait_for_timeout(2000)
            is_map_visible = await page.is_visible('#view-map:not(.hidden)')
            print(f'🌍 View Mapa Visível: {is_map_visible}')

            await asyncio.sleep(10) # Tempo para inspeção humana

        except Exception as e:
            print(f'❌ Erro no teste: {e}')
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_ui_test())
