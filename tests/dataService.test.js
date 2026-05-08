import { test, expect } from '@playwright/test';

test.describe('dataService - Worker Metrics', () => {
    test('deve ter os métodos de métricas de workers definidos', async ({ page }) => {
        // Vai para uma página em branco e injeta as dependências mínimas ou vai para a home
        await page.goto('http://localhost:3000'); // Assume o servidor dev está rodando
        
        const methodsExist = await page.evaluate(() => {
            // No contexto do navegador, o dataService deve estar disponível se o bundle carregou
            // Mas como é um módulo, talvez não esteja no window. 
            // Vamos tentar importar ou verificar se o app.js já o exportou para o window para debug
            return typeof window.dataService !== 'undefined' &&
                   typeof window.dataService.getWorkersMetrics === 'function' &&
                   typeof window.dataService.getWorkersCredits === 'function';
        });
        
        // Se não estiver no window, vamos injetar um script que importa o serviço
        if (!methodsExist) {
            const injectedExists = await page.evaluate(async () => {
                const { dataService } = await import('./src/services/dataService.js');
                return typeof dataService.getWorkersMetrics === 'function' &&
                       typeof dataService.getWorkersCredits === 'function';
            });
            expect(injectedExists).toBe(true);
        } else {
            expect(methodsExist).toBe(true);
        }
    });
});
