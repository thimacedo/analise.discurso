import { test, expect } from '@playwright/test';

test('Sentinela v15 UI Check', async ({ page }) => {
  // Como não temos um servidor rodando agora, vamos assumir que o teste será rodado em ambiente de CI/CD
  // ou que o usuário quer que verifiquemos a estrutura do HTML diretamente.
  // Para este ambiente Gemini, vamos simular a navegação se o arquivo index.html estiver acessível via file://
  
  const filePath = `file://${process.cwd().replace(/\\/g, '/')}/index.html`;
  await page.goto(filePath);

  // 1. Verificar Título
  await expect(page).toHaveTitle(/SENTINELA/);

  // 2. Verificar se mudamos para "Monitorados"
  const monitoradosText = await page.textContent('body');
  expect(monitoradosText).toContain('Monitorados');
  expect(monitoradosText).not.toContain('Dossiê monitorados'); // Deve ter mudado para Dossiê Monitorados

  // 3. Verificar Visibilidade do Mapa
  const map = page.locator('#svg-map-br');
  await expect(map).toBeVisible();

  // 4. Testar abertura do Checkout (Deve estar oculto inicialmente)
  const checkout = page.locator('#checkout-modal');
  await expect(checkout).toBeHidden();

  // 5. Clicar em Exportar e verificar se Checkout abre
  await page.click('button:has-text("Exportar Inteligência")');
  await expect(checkout).toBeVisible();
});
