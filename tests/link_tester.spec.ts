import { test, expect } from '@playwright/test';

const PRODUCTION_URL = 'https://sentinela-democratica-ruby.vercel.app';

test.describe('SENTINELA | Diamond Edition - Link & Routing Tests', () => {
    test.setTimeout(60000);

    test('deve navegar por todas as abas e filtros sem erros', async ({ page }) => {
        await page.goto(PRODUCTION_URL);

        // Aguarda carregamento inicial
        await page.waitForSelector('#kpi-monitorados:not(:has-text("---"))', { timeout: 30000 });

        // Lista de views
        const views = [
            { id: 'nav-networks', hash: '#networks', section: '#view-networks' },
            { id: 'nav-directory', hash: '#directory', section: '#view-directory' },
            { id: 'nav-dossie', hash: '#dossie', section: '#view-dossie' },
            { id: 'nav-map', hash: '#map', section: '#view-map' },
            { id: 'nav-monitor', hash: '#monitor', section: '#view-monitor' } // Voltar ao início
        ];

        for (const v of views) {
            console.log(`Testando link: ${v.id}`);
            await page.click(`#${v.id}`);
            await expect(page).toHaveURL(new RegExp(`${v.hash}$`));
            await expect(page.locator(v.section)).toHaveClass(/active-view/);
            // Pequeno delay para a transição
            await page.waitForTimeout(500);
        }

        // Lista de filtros
        const filters = ['btn-filter-hate', 'btn-filter-critical', 'btn-filter-all'];
        for (const f of filters) {
            console.log(`Testando filtro: ${f}`);
            await page.click(`#${f}`);
            // Verifica se o botão ficou ativo
            await expect(page.locator(`#${f}`)).toHaveClass(/active/);
            await page.waitForTimeout(500);
        }

        // Verifica se há erros no console durante a navegação
        const errors = [];
        page.on('pageerror', error => errors.push(error.message));
        page.on('console', msg => {
            if (msg.type() === 'error') errors.push(msg.text());
        });

        expect(errors).toHaveLength(0);
        console.log('Navegação concluída com sucesso! Todos os links e filtros estão operacionais.');
    });
});
