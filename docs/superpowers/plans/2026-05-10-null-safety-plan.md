# Plano de Implementação: [STN-001] Resiliência do Frontend (Null-Safety)

> **Para agentes de trabalho:** HABILIDADE REQUERIDA: Use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para implementar este plano tarefa por tarefa. As etapas usam a sintaxe de caixa de seleção (`- [ ]`) para rastreamento.

**Meta:** Garantir que a UI do Sentinela Democrática não quebre ao receber `null`, `undefined` ou respostas de erro das chamadas de API para `summary`, `targets`, e `alerts`.

**Arquitetura:** A correção será focada no frontend, especificamente nos arquivos que consomem os dados da API (`app.js`) e nos que os renderizam (`ui.js`). Vamos interceptar os dados após o `Promise.all` e garantir que valores nulos ou de erro sejam substituídos por "estados seguros" (ex: objetos vazios ou arrays vazios) antes de serem passados para as funções de renderização.

**Tech Stack:** JavaScript (Vanilla)

---

### Tarefa 1: Garantir Null-Safety na Carga Inicial de Dados

**Arquivos:**
- Modify: `src/core/app.js`

- [ ] **Passo 1: Modificar o tratamento de resposta da API em `initDashboard`**
  No arquivo `src/core/app.js`, localize a função `initDashboard`. Altere o bloco `Promise.all` para garantir que, em caso de falha, `summary` receba um objeto vazio, e `targets` e `alerts` recebam arrays vazios.

  Executar: `replace`
  - **file_path**: `src/core/app.js`
  - **old_string**:
  ```javascript
        const [summary, targets, alerts] = await Promise.all([
            dataService.getSummary().catch(() => ({ error: true })),
            dataService.getTargets().catch(() => []),
            dataService.getAlerts(20, 1).catch(() => [])
        ]);
  ```
  - **new_string**:
  ```javascript
        const [summary, targets, alerts] = await Promise.all([
            dataService.getSummary().catch(() => ({})), // Retorna objeto vazio em caso de erro
            dataService.getTargets().catch(() => []),   // Retorna array vazio em caso de erro
            data.getAlerts(20, 1).catch(() => [])       // Retorna array vazio em caso de erro
        ]);
  ```

- [ ] **Passo 2: Refatorar a atualização do estado para ser mais resiliente**
  Ainda em `src/core/app.js`, dentro de `initDashboard`, simplifique a lógica que atualiza o estado, aproveitando os valores padrão seguros definidos no passo anterior.

  Executar: `replace`
  - **file_path**: `src/core/app.js`
  - **old_string**:
  ```javascript
        state.data = Array.isArray(targets) ? targets : [];
        state.alertas = Array.isArray(alerts) ? alerts : [];

        if (summary && !summary.error) {
            state.summary = { ...summary };
        } else {
            state.summary = {
                total_monitorados: 0,
                total_alertas: 0,
                total_amostra: 0,
                resiliencia: 0,
            };
        }
  ```
  - **new_string**:
  ```javascript
        state.data = targets;
        state.alertas = alerts;
        state.summary = summary;
  ```

- [ ] **Passo 3: Adicionar fallback na renderização dos KPIs**
  Ainda em `src/core/app.js`, adicione fallbacks (operador `||`) ao atualizar os elementos da UI para garantir que, se `state.summary` for um objeto vazio, os valores padrão `0` ou `---` sejam exibidos.

  Executar: `replace`
  - **file_path**: `src/core/app.js`
  - **old_string**:
  ```javascript
        updateEl('kpi-monitorados', state.summary.total_monitorados);
        updateEl('kpi-time-monitorados', 'agora');
        updateEl('kpi-hate', state.summary.total_alertas);
        updateEl('kpi-time-hate', 'agora');
        updateEl('kpi-total', state.summary.total_amostra.toLocaleString('pt-BR'));
        updateEl('kpi-time-total', 'agora');
        updateEl('kpi-res', `${state.summary.resiliencia}%`);
        updateEl('kpi-time-res', 'agora');
  ```
  - **new_string**:
  ```javascript
        updateEl('kpi-monitorados', state.summary?.total_monitorados || '---');
        updateEl('kpi-time-monitorados', 'agora');
        updateEl('kpi-hate', state.summary?.total_alertas || '---');
        updateEl('kpi-time-hate', 'agora');
        updateEl('kpi-total', state.summary?.total_amostra?.toLocaleString('pt-BR') || '---');
        updateEl('kpi-time-total', 'agora');
        updateEl('kpi-res', `${state.summary?.resiliencia || 0}%`);
        updateEl('kpi-time-res', 'agora');
  ```

- [ ] **Passo 4: Commitar as alterações de `app.js`**
  Executar: `run_shell_command(command='git add src/core/app.js && git commit -m "feat(app): add null-safety to initDashboard"', description='Commitar as alterações de null-safety em app.js.')`


### Tarefa 2: Garantir Null-Safety na Renderização da UI

**Arquivos:**
- Modify: `src/core/ui.js`

- [ ] **Passo 1: Simplificar a função `renderAll`**
  No arquivo `src/core/ui.js`, a função `renderAll` já possui alguma lógica de segurança. Vamos simplificá-la para confiar nos valores padrão fornecidos por `app.js`.

  Executar: `replace`
  - **file_path**: `src/core/ui.js`
  - **old_string**:
  ```javascript
export function renderAll(summary = {}, targets = [], alerts = []) {
    const safeSummary = summary || {};
    const safeTargets = Array.isArray(targets) ? targets : [];
    const safeAlerts = Array.isArray(alerts) ? alerts : [];

    renderFeed(safeAlerts);
    renderPrioridade(safeTargets);
}
  ```
  - **new_string**:
  ```javascript
export function renderAll(summary = {}, targets = [], alerts = []) {
    renderFeed(alerts);
    renderPrioridade(targets);
}
  ```
- [ ] **Passo 2: Simplificar a função `renderFeed`**
  Ainda em `src/core/ui.js`, a função `renderFeed` também pode ser simplificada.

  Executar: `replace`
  - **file_path**: `src/core/ui.js`
  - **old_string**:
  ```javascript
export function renderFeed(alertas, containerId = 'feed-alertas', append = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const safeAlerts = Array.isArray(alertas) ? alertas : [];

    if (safeAlerts.length === 0 && !append) {
        container.innerHTML = '<div class="p-4 text-center text-slate-400 text-sm">Nenhum alerta encontrado.</div>';
        return;
    }
  ```
  - **new_string**:
  ```javascript
export function renderFeed(alertas = [], containerId = 'feed-alertas', append = false) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (alertas.length === 0 && !append) {
        container.innerHTML = '<div class="p-4 text-center text-slate-400 text-sm">Nenhum alerta encontrado.</div>';
        return;
    }
  ```

- [ ] **Passo 3: Commitar as alterações de `ui.js`**
  Executar: `run_shell_command(command='git add src/core/ui.js && git commit -m "refactor(ui): simplify render functions with null-safety"', description='Commitar as refatorações de null-safety em ui.js.')`

### Tarefa 3: Verificação Final

- [ ] **Passo 1: Rodar o build da aplicação**
  Executar o comando de build para garantir que não há erros de sintaxe.
  Executar: `run_shell_command(command='npm run build', description='Build da aplicação para validar as alterações.')`

- [ ] **Passo 2: (Manual) Teste visual**
  Rodar `npm run dev` e verificar a aplicação no navegador, especialmente em cenários onde a API pode falhar (simular com bloqueio de rede no DevTools), para confirmar que a UI se mantém estável.
