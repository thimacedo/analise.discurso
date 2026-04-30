# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests\diamond_smoke.spec.ts >> SENTINELA | Diamond Edition - Smoke Tests >> deve exibir o modal de upgrade ao tentar acessar funcionalidade Pro (Gating)
- Location: tests\diamond_smoke.spec.ts:45:9

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator:  locator('#upgrade-modal')
Expected: visible
Received: hidden
Timeout:  5000ms

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('#upgrade-modal')
    9 × locator resolved to <div id="upgrade-modal" class="modal-overlay">…</div>
      - unexpected value "hidden"

```

# Page snapshot

```yaml
- generic [ref=e1]:
  - complementary [ref=e2]:
    - generic [ref=e3]:
      - img "Logo Sentinela" [ref=e5]
      - generic [ref=e6]:
        - heading "Sentinela" [level=1] [ref=e7]
        - text: Diamond v19.6.1
        - generic [ref=e8]:
          - img [ref=e9]
          - generic [ref=e11]: 0 STN
    - navigation [ref=e12]:
      - link "Panorama Global" [ref=e13] [cursor=pointer]:
        - /url: "#monitor"
        - img [ref=e14]
        - text: Panorama Global
      - link "Inteligência de Redes" [active] [ref=e19] [cursor=pointer]:
        - /url: "#networks"
        - img [ref=e20]
        - text: Inteligência de Redes
      - link "Dossiê de Alvos" [ref=e26] [cursor=pointer]:
        - /url: "#dossie"
        - img [ref=e27]
        - text: Dossiê de Alvos
      - link "Geopolítica UF" [ref=e36] [cursor=pointer]:
        - /url: "#map"
        - img [ref=e37]
        - text: Geopolítica UF
    - generic [ref=e40]:
      - generic [ref=e41]: Aguardando leitura...
      - button "Sincronizar Dados" [ref=e42] [cursor=pointer]
  - main [ref=e43]:
    - generic [ref=e45]: Sinal Operacional
    - generic [ref=e46]:
      - generic [ref=e47]:
        - text: Monitorados
        - generic [ref=e48]: "---"
      - generic [ref=e49]:
        - text: Alertas PASA
        - generic [ref=e50]: "---"
      - generic [ref=e51]:
        - text: Amostragem
        - generic [ref=e52]: "---"
      - generic [ref=e53]:
        - text: Resiliência
        - generic [ref=e54]: "---"
    - generic [ref=e56]:
      - img [ref=e58]
      - heading "Inteligência de Redes" [level=3] [ref=e61]
      - paragraph [ref=e62]: A detecção de redes coordenadas é exclusiva para o plano Enterprise.
      - button "Fazer Upgrade →" [ref=e63] [cursor=pointer]
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
  14 |         await expect(page).toHaveTitle(/SENTINELA | Diamond Edition/);
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
  30 |         const triagemItems = page.locator('.monitor-row');
  31 |         await expect(triagemItems.first()).toBeVisible();
  32 |         const countTriagem = await triagemItems.count();
  33 |         console.log(`Total de alvos carregados na triagem: ${countTriagem}`);
  34 |         expect(countTriagem).toBeGreaterThan(0);
  35 | 
  36 |         // 5. Verifica se o feed de alertas está visível e populado (se houver ódio)
  37 |         const feedAlertas = page.locator('#feed-alertas');
  38 |         await expect(feedAlertas).toBeVisible();
  39 |         
  40 |         // 6. Verifica se o mapa geopolítico carregou (o SVG deve estar presente)
  41 |         const mapaSvg = page.locator('#svg-map-br svg');
  42 |         await expect(mapaSvg).toBeVisible();
  43 |     });
  44 | 
  45 |     test('deve exibir o modal de upgrade ao tentar acessar funcionalidade Pro (Gating)', async ({ page }) => {
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
> 60 |         await expect(upgradeModal).toBeVisible();
     |                                    ^ Error: expect(locator).toBeVisible() failed
  61 |         await expect(page.locator('.upgrade-gate')).toBeVisible();
  62 |     });
  63 | 
  64 | });
  65 | 
```