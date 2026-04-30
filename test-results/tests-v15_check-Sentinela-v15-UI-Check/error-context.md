# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: tests\v15_check.spec.ts >> Sentinela v15 UI Check
- Location: tests\v15_check.spec.ts:3:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('#svg-map-br')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('#svg-map-br')

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - complementary [ref=e2]:
    - generic [ref=e3]:
      - img "Logo Sentinela" [ref=e5]
      - generic [ref=e6]:
        - heading "Sentinela" [level=1] [ref=e7]
        - text: Diamond v19.6.1
        - generic [ref=e10]: "-- STN"
    - navigation [ref=e11]:
      - link "Panorama Global" [ref=e12] [cursor=pointer]:
        - /url: "#monitor"
        - text: Panorama Global
      - link "Inteligência de Redes" [ref=e13] [cursor=pointer]:
        - /url: "#networks"
        - text: Inteligência de Redes
      - link "Dossiê de Alvos" [ref=e14] [cursor=pointer]:
        - /url: "#dossie"
        - text: Dossiê de Alvos
      - link "Geopolítica UF" [ref=e15] [cursor=pointer]:
        - /url: "#map"
        - text: Geopolítica UF
    - generic [ref=e16]:
      - text: Conectado ao Proxy...
      - button "Sincronizar Dados" [ref=e17] [cursor=pointer]
  - main [ref=e18]:
    - generic [ref=e20]: Sinal Operacional
    - generic [ref=e21]:
      - generic [ref=e22]:
        - text: Monitorados
        - generic [ref=e23]: "---"
      - generic [ref=e24]:
        - text: Alertas PASA
        - generic [ref=e25]: "---"
      - generic [ref=e26]:
        - text: Amostragem
        - generic [ref=e27]: "---"
      - generic [ref=e28]:
        - text: Resiliência
        - generic [ref=e29]: "---"
    - generic [ref=e31]:
      - generic [ref=e35]:
        - text: Linha do Tempo
        - heading "Evidências PASA" [level=3] [ref=e36]
      - generic [ref=e39]:
        - text: Análise de Risco
        - heading "Prioridade de Triagem" [level=3] [ref=e40]
```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test';
  2  | 
  3  | test('Sentinela v15 UI Check', async ({ page }) => {
  4  |   // Como não temos um servidor rodando agora, vamos assumir que o teste será rodado em ambiente de CI/CD
  5  |   // ou que o usuário quer que verifiquemos a estrutura do HTML diretamente.
  6  |   // Para este ambiente Gemini, vamos simular a navegação se o arquivo index.html estiver acessível via file://
  7  |   
  8  |   const filePath = `file://${process.cwd().replace(/\\/g, '/')}/index.html`;
  9  |   await page.goto(filePath);
  10 | 
  11 |   // 1. Verificar Título
  12 |   await expect(page).toHaveTitle(/SENTINELA/);
  13 | 
  14 |   // 2. Verificar se mudamos para "Monitorados"
  15 |   const monitoradosText = await page.textContent('body');
  16 |   expect(monitoradosText).toContain('Monitorados');
  17 |   expect(monitoradosText).not.toContain('Dossiê monitorados'); // Deve ter mudado para Dossiê Monitorados
  18 | 
  19 |   // 3. Verificar Visibilidade do Mapa
  20 |   const map = page.locator('#svg-map-br');
> 21 |   await expect(map).toBeVisible();
     |                     ^ Error: expect(locator).toBeVisible() failed
  22 | 
  23 |   // 4. Testar abertura do Checkout (Deve estar oculto inicialmente)
  24 |   const checkout = page.locator('#checkout-modal');
  25 |   await expect(checkout).toBeHidden();
  26 | 
  27 |   // 5. Clicar em Exportar e verificar se Checkout abre
  28 |   await page.click('button:has-text("Exportar Inteligência")');
  29 |   await expect(checkout).toBeVisible();
  30 | });
  31 | 
```