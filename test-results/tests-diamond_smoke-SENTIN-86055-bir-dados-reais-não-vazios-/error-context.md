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
    33 × locator resolved to <div class="kpi-value" id="kpi-monitorados">---</div>
       - unexpected value "---"

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - complementary [ref=e2]:
    - generic [ref=e3]:
      - img "Logo Sentinela" [ref=e5]
      - generic [ref=e6]:
        - heading "Sentinela" [level=1] [ref=e7]
        - text: Diamond v17.2
    - navigation [ref=e8]:
      - link "Panorama Global" [ref=e9] [cursor=pointer]:
        - /url: "#monitor"
        - img [ref=e10]
        - text: Panorama Global
      - link "Inteligência de Redes" [ref=e15] [cursor=pointer]:
        - /url: "#networks"
        - img [ref=e16]
        - text: Inteligência de Redes
      - link "Dossiê de Alvos" [ref=e22] [cursor=pointer]:
        - /url: "#dossie"
        - img [ref=e23]
        - text: Dossiê de Alvos
      - link "Geopolítica UF" [ref=e32] [cursor=pointer]:
        - /url: "#map"
        - img [ref=e33]
        - text: Geopolítica UF
    - generic [ref=e36]:
      - generic [ref=e37]: Aguardando leitura...
      - button "Sincronizar Banco" [ref=e38] [cursor=pointer]
  - main [ref=e39]:
    - generic [ref=e41]: Sinal Operacional
    - generic [ref=e42]:
      - generic [ref=e43]:
        - text: Monitorados
        - generic [ref=e44]: "---"
      - generic [ref=e45]:
        - text: Alertas PASA
        - generic [ref=e46]: "---"
      - generic [ref=e47]:
        - text: Amostragem
        - generic [ref=e48]: "---"
      - generic [ref=e49]:
        - text: Resiliência
        - generic [ref=e50]: "---"
    - generic [ref=e52]:
      - generic [ref=e53]:
        - generic [ref=e54]:
          - generic [ref=e55]:
            - generic [ref=e56]:
              - text: Linha do Tempo
              - heading "Evidências de Ataque" [level=3] [ref=e57]
            - generic [ref=e58]: Monitoramento em tempo real dos sinais de hostilidade.
          - generic [ref=e60]:
            - img [ref=e62]
            - strong [ref=e65]: Nenhum alerta ativo
            - paragraph [ref=e66]: Sem sinais críticos para este filtro.
        - generic [ref=e69]: Insights Rápidos
      - generic [ref=e71]:
        - generic [ref=e72]:
          - text: Análise de Risco
          - heading "Prioridade de Triagem" [level=3] [ref=e73]
        - generic [ref=e74]: Selecione o alvo para isolar as evidências.
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
  60 |         await expect(upgradeModal).toBeVisible();
  61 |         await expect(page.locator('.upgrade-gate')).toBeVisible();
  62 |     });
  63 | 
  64 | });
  65 | 
```