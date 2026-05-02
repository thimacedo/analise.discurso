# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests\diamond_smoke.spec.ts >> SENTINELA | Diamond Edition - Smoke Tests >> deve carregar o dashboard e exibir dados reais (não vazios)
- Location: tests\diamond_smoke.spec.ts:7:9

# Error details

```
Error: expect(locator).not.toHaveText(expected) failed

Locator:  locator('#kpi-monitorados')
Expected: not "---"
Received: "---"
Timeout:  30000ms

Call log:
  - Expect "not toHaveText" with timeout 30000ms
  - waiting for locator('#kpi-monitorados')
    2 × locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
      - unexpected value "---"
      - locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
      - unexpected value "---"
      - waiting for" https://sentinela-democratica-ruby.vercel.app/" navigation to finish...
      - navigated to "https://sentinela-democratica-ruby.vercel.app/#monitor"
    3 × locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
      - unexpected value "---"
      - waiting for" https://sentinela-democratica-ruby.vercel.app/" navigation to finish...
      - navigated to "https://sentinela-democratica-ruby.vercel.app/#monitor"
    5 × locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
      - unexpected value "---"
    - waiting for" https://sentinela-democratica-ruby.vercel.app/" navigation to finish...
    - navigated to "https://sentinela-democratica-ruby.vercel.app/#monitor"
    3 × locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
      - unexpected value "---"
    2 × waiting for" https://sentinela-democratica-ruby.vercel.app/" navigation to finish...
      - navigated to "https://sentinela-democratica-ruby.vercel.app/#monitor"
      - locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
      - unexpected value "---"
      - locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
      - unexpected value "---"
    6 × locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
      - unexpected value "---"
    3 × waiting for" https://sentinela-democratica-ruby.vercel.app/" navigation to finish...
      - navigated to "https://sentinela-democratica-ruby.vercel.app/#monitor"
      - locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
      - unexpected value "---"
    - locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
    - unexpected value "---"
    - waiting for navigation to finish...
    - navigated to "https://sentinela-democratica-ruby.vercel.app/#monitor"
    2 × locator resolved to <div id="kpi-monitorados" class="text-sm font-black text-slate-800">---</div>
      - unexpected value "---"

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - complementary [ref=e2]:
    - generic [ref=e3]:
      - img "Logo" [ref=e5]
      - heading "Sentinela" [level=1] [ref=e6]
    - navigation [ref=e7]:
      - textbox "Pesquisar..." [ref=e10]
      - link "Panorama" [ref=e11] [cursor=pointer]:
        - /url: "#monitor"
        - generic [ref=e12]: Panorama
      - link "Redes" [ref=e13] [cursor=pointer]:
        - /url: "#networks"
        - generic [ref=e14]: Redes
      - link "Perfis" [ref=e15] [cursor=pointer]:
        - /url: "#directory"
        - generic [ref=e16]: Perfis
      - link "Dossiês" [ref=e17] [cursor=pointer]:
        - /url: "#dossie"
        - generic [ref=e18]: Dossiês
      - link "Mapa" [ref=e19] [cursor=pointer]:
        - /url: "#map"
        - generic [ref=e20]: Mapa
      - generic [ref=e21]:
        - text: Filtros de Inteligência
        - button "Global" [ref=e22] [cursor=pointer]:
          - generic [ref=e23]: Global
        - button "Alertas" [ref=e24] [cursor=pointer]:
          - generic [ref=e25]: Alertas
        - button "Crítico" [ref=e26] [cursor=pointer]:
          - generic [ref=e27]: Crítico
  - main [ref=e28]
  - complementary [ref=e32]:
    - generic [ref=e33]:
      - img "Logo" [ref=e35]
      - generic [ref=e36]:
        - heading "Sentinela Diamond" [level=2] [ref=e37]
        - text: 0 STN
    - generic [ref=e38]:
      - generic [ref=e39]:
        - text: Alvos
        - generic [ref=e40]: "---"
      - generic [ref=e41]:
        - text: Alertas
        - generic [ref=e42]: "---"
      - generic [ref=e43]:
        - text: Amostra
        - generic [ref=e44]: "---"
      - generic [ref=e45]:
        - text: Resiliência
        - generic [ref=e46]: "---"
    - generic [ref=e47]:
      - heading "Publicidade Estratégica" [level=3] [ref=e48]
      - insertion [ref=e50]:
        - iframe [ref=e52]:
          
    - heading "Prioridade de Triagem" [level=3] [ref=e54]
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
  8  |         // Aumenta o timeout para lidar com o cold start
  9  |         test.setTimeout(60000);
  10 | 
  11 |         await page.goto(PRODUCTION_URL);
  12 | 
  13 |         // 1. Verifica o Título
  14 |         await expect(page).toHaveTitle(/SENTINELA | Diamond Edition/);
  15 | 
  16 |         // 2. Aguarda o desaparecimento do estado inicial '---' nos KPIs
  17 |         const kpiMonitorados = page.locator('#kpi-monitorados');
  18 |         const kpiAlertas = page.locator('#kpi-hate');
  19 |         
  20 |         // Aguarda até que o texto não seja mais '---' (timeout de 30s automático do Playwright)
> 21 |         await expect(kpiMonitorados).not.toHaveText('---', { timeout: 30000 });
     |                                          ^ Error: expect(locator).not.toHaveText(expected) failed
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