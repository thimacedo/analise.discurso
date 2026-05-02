import { test, expect } from '@playwright/test';

const PRODUCTION_URL = 'https://sentinela-democratica-ruby.vercel.app';

test.describe('SENTINELA | Diamond Edition - Smoke Tests', () => {

    test('deve carregar o dashboard e exibir dados reais (não vazios)', async ({ page }) => {
        // Aumenta o timeout para lidar com o cold start
        test.setTimeout(60000);

        await page.goto(PRODUCTION_URL);

        // 1. Verifica o Título
        await expect(page).toHaveTitle(/SENTINELA | Diamond Edition/);

        // 2. Aguarda o desaparecimento do estado inicial '---' nos KPIs
        const kpiMonitorados = page.locator('#kpi-monitorados');
        const kpiAlertas = page.locator('#kpi-hate');
        
        // Aguarda até que o texto não seja mais '---' (timeout de 30s automático do Playwright)
        await expect(kpiMonitorados).not.toHaveText('---', { timeout: 30000 });
        await expect(kpiAlertas).not.toHaveText('---');

        // 3. Valida se os valores são numéricos (ou contêm K/M)
        const valorMonitorados = await kpiMonitorados.innerText();
        console.log(`KPI Monitorados: ${valorMonitorados}`);
        expect(valorMonitorados).not.toBe('');
        
        // 4. Verifica se a lista de triagem (Priority List) carregou
        const triagemItems = page.locator('.target-card, .monitor-row');
        await expect(triagemItems.first()).toBeVisible({ timeout: 15000 });
        const countTriagem = await triagemItems.count();
        console.log(`Total de alvos carregados na triagem: ${countTriagem}`);
        expect(countTriagem).toBeGreaterThan(0);

        // 5. Verifica se o feed de alertas está visível e populado (se houver ódio)
        const feedAlertas = page.locator('#feed-alertas');
        await expect(feedAlertas).toBeVisible();

        // 6. Verifica se o mapa geopolítico carregou (o SVG deve estar presente)
        // const mapaSvg = page.locator('#svg-map-br svg');
        // await expect(mapaSvg).toBeVisible();
        });

        test.skip('deve exibir o modal de upgrade ao tentar acessar funcionalidade Pro (Gating)', async ({ page }) => {
        await page.goto(PRODUCTION_URL);

        // Simula o plano public se necessário via injeção de script ou apenas clica em funcionalidade restrita
        // Como o mock atual é 'pro', vamos forçar 'public' para o teste de fumaça de gating
        await page.addInitScript(() => {
            window.SENTINELA_USER = { plan: 'public' };
        });
        await page.reload();

        // Tenta ir para a aba de Redes (que é restrita)
        await page.click('a[href="#networks"]');

        // Verifica se o modal de upgrade apareceu
        const upgradeModal = page.locator('#upgrade-modal');
        await expect(upgradeModal).toBeVisible();
        await expect(page.locator('.upgrade-gate')).toBeVisible();
    });

});
