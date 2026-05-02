# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests\diamond_smoke.spec.ts >> SENTINELA | Diamond Edition - Smoke Tests >> deve carregar o dashboard e exibir dados reais (não vazios)
- Location: tests\diamond_smoke.spec.ts:7:9

# Error details

```
Error: expect(page).toHaveTitle(expected) failed

Expected pattern: /SENTINELA | Diamond Edition/
Received string:  "404: NOT_FOUND"
Timeout: 5000ms

Call log:
  - Expect "toHaveTitle" with timeout 5000ms
    8 × unexpected value "404: NOT_FOUND"

```

# Page snapshot

```yaml
- main [ref=e3]:
  - paragraph [ref=e4]:
    - generic [ref=e5]:
      - strong [ref=e6]: "404"
      - text: ": NOT_FOUND"
    - generic [ref=e7]:
      - text: "Code:"
      - code [ref=e8]: "`NOT_FOUND`"
    - generic [ref=e9]:
      - text: "ID:"
      - code [ref=e10]: "`gru1::gk44p-1777747681020-51f32ee681c4`"
  - link "Read our documentation to learn more about this error." [ref=e11] [cursor=pointer]:
    - /url: https://vercel.com/docs/errors/NOT_FOUND
    - generic [ref=e12]: Read our documentation to learn more about this error.
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | const PRODUCTION_URL = 'https://sentinela-democratica-ruby.vercel.app';
  4  | 
  5  | test.describe('SENTINELA | Diamond Edition - Smoke Tests', () => {
  6  | 
  7  |     test('deve carregar o dashboard e exibir dados reais (não vazios)', async ({ page }) => {
  8  |         // Aumenta o timeout para lidar com o cold start da API na Vercel
  9  |         test.setTimeout(60000);
  10 | 
  11 |         await page.goto(PRODUCTION_URL);
  12 | 
  13 |         // 1. Verifica o Título
> 14 |         await expect(page).toHaveTitle(/SENTINELA | Diamond Edition/);
     |                            ^ Error: expect(page).toHaveTitle(expected) failed
  15 | 
  16 |         // 2. Aguarda o desaparecimento do estado inicial '---' nos KPIs
  17 |         const kpiMonitorados = page.locator('#kpi-monitorados');
  18 |         const kpiAlertas = page.locator('#kpi-hate');
  19 |         
  20 |         // Aguarda até que o texto não seja mais '---' (timeout de 30s automático do Playwright)
  21 |         await expect(kpiMonitorados).not.toHaveText('---', { timeout: 30000 });
  22 |         await expect(kpiAlertas).not.toHaveText('---');
  23 | 
  24 |         // 3. Valida se os valores são numéricos (ou contêm K/M)
  25 |         const valorMonitorados = await kpiMonitorados.innerText();
  26 |         console.log(`KPI Monitorados: ${valorMonitorados}`);
  27 |         expect(valorMonitorados).not.toBe('');
  28 |         
  29 |         // 4. Verifica se a lista de triagem (Priority List) carregou
  30 |         const triagemItems = page.locator('.target-card, .monitor-row');
  31 |         await expect(triagemItems.first()).toBeVisible({ timeout: 15000 });
  32 |         const countTriagem = await triagemItems.count();
  33 |         console.log(`Total de alvos carregados na triagem: ${countTriagem}`);
  34 |         expect(countTriagem).toBeGreaterThan(0);
  35 | 
  36 |         // 5. Verifica se o feed de alertas está visível e populado (se houver ódio)
  37 |         const feedAlertas = page.locator('#feed-alertas');
  38 |         await expect(feedAlertas).toBeVisible();
  39 | 
  40 |         // 6. Verifica se o mapa geopolítico carregou (o SVG deve estar presente)
  41 |         // const mapaSvg = page.locator('#svg-map-br svg');
  42 |         // await expect(mapaSvg).toBeVisible();
  43 |         });
  44 | 
  45 |         test.skip('deve exibir o modal de upgrade ao tentar acessar funcionalidade Pro (Gating)', async ({ page }) => {
  46 |         await page.goto(PRODUCTION_URL);
  47 | 
  48 |         // Simula o plano public se necessário via injeção de script ou apenas clica em funcionalidade restrita
  49 |         // Como o mock atual é 'pro', vamos forçar 'public' para o teste de fumaça de gating
  50 |         await page.addInitScript(() => {
  51 |             window.SENTINELA_USER = { plan: 'public' };
  52 |         });
  53 |         await page.reload();
  54 | 
  55 |         // Tenta ir para a aba de Redes (que é restrita)
  56 |         await page.click('a[href="#networks"]');
  57 | 
  58 |         // Verifica se o modal de upgrade apareceu
  59 |         const upgradeModal = page.locator('#upgrade-modal');
  60 |         await expect(upgradeModal).toBeVisible();
  61 |         await expect(page.locator('.upgrade-gate')).toBeVisible();
  62 |     });
  63 | 
  64 | });
  65 | 
```