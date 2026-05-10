# Tickets Consolidados - Sessões de 09/05/2026

## Épico Recente: Sentinela Enterprise
### [epic_cicd] CI/CD Quality Gates (Ruff, Black, ESLint, GitHub Actions)
**Status:** Todo (Plano Aprovado)
**Objetivo:** Implementar pipeline no GitHub Actions para PRs na branch main e adicionar configurações estritas de Ruff, Black e ESLint do zero.

---

## Tickets de Implementação - Milestone v20.6 (STN-001 a STN-007)

### [STN-001] Resiliência da UI e Null-Safety (P0)
**Objetivo:** Impedir o colapso do frontend (ecrã branco) quando a API falha.
**Arquivos de Interesse:** `src/core/app.js`, `src/core/ui.js`.
**Critérios de Aceitação:**
- Implementação de fallbacks (`|| []`, `|| {}`) em todas as variáveis que vêm da API.
- Substituição de acessos diretos por Optional Chaining (`?.`).
- Injeção de Empty States/Mensagens de Erro amigáveis no DOM.

### [STN-002] Otimização de Memória e Paginação (P0)
**Objetivo:** Corrigir o estouro de memória (OOM) no Node.js e navegador.
**Arquivos de Interesse:** `src/services/dataService.js`, `src/core/app.js`.
**Critérios de Aceitação:**
- Limitar o carregamento inicial de alertas e alvos a 20 itens.
- Garantir que o `Infinite Scroll` use parâmetros de paginação corretos.
- Validar se a Heap de memória do navegador permanece estável após 3 ciclos de scroll.

### [STN-003] Estratégia de Cache Busting (P1)
**Objetivo:** Garantir que o cliente receba sempre a versão mais nova do frontend.
**Arquivos de Interesse:** `index.html`, `vercel.json`.
**Critérios de Aceitação:**
- Adicionar query string de versão (`?v=20.6.0`) nas importações de scripts.
- Configurar `vercel.json` com cabeçalhos `Cache-Control: no-cache` para arquivos JS.

### [STN-004] Correção de IDs de Monetização (P0)
**Objetivo:** Ativar AdSense e Stripe com IDs de produção funcionais.
**Arquivos de Interesse:** `index.html`, `src/core/ui.js`, `src/core/payments.js`.
**Critérios de Aceitação:**
- Substituir `SIDEBAR_DIAMOND` por ID numérico real.
- Substituir `price_1Starter` por ID de produção do Stripe.
- Garantir que os anúncios não quebrem o layout do feed.

### [STN-005] Robustez de Scraping e Regex Fallback (P1)
**Objetivo:** Evitar perda de dados por mudanças no DOM das redes sociais.
**Arquivos de Interesse:** `core/instagram_headless.py` (ou correspondente), `api/index.py`.
**Critérios de Aceitação:**
- Implementar extração via Regex caso os seletores CSS falhem.
- Garantir que o `texto_bruto` nunca seja nulo se houver texto na postagem.

### [STN-006] Consolidação e Purga de Workers (P1)
**Objetivo:** Eliminar redundâncias e limpar o código de workers obsoletos.
**Arquivos de Interesse:** `api/index.py`, `core/` (pasta de workers).
**Critérios de Aceitação:**
- Mapear todos os workers ativos e inativos.
- Deletar `main_orchestrator.py` e `official_solenya_daemon.py`.
- Unificar lógica no `orquestrador.py`.
- Limpar variáveis de ambiente e imports órfãos.

### [STN-007] Otimização de Carregamento do Panorama (P0)
**Objetivo:** Reduzir o tempo de carregamento inicial da tela Panorama.
**Arquivos de Interesse:** `src/services/dataService.js`, `api/index.py`.
**Critérios de Aceitação:**
- Limite de 20 itens no fetch inicial de alvos e alertas (Concluído no frontend).
- Otimizar query SQL no backend para retornar apenas o necessário para o Panorama.
- Implementar cache agressivo (SWR ou similar) para dados estáticos de alvos.