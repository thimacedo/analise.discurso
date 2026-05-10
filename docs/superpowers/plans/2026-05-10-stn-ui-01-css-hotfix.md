# Plano de Implementação: [STN-UI-01] Ressuscitar CSS (Hotfix Tailwind/CDN)

> **Para agentes de trabalho:** HABILIDADE REQUERIDA: Use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para implementar este plano tarefa por tarefa. As etapas usam a sintaxe de caixa de seleção (`- [ ]`) para rastreamento.

**Meta:** Restaurar a funcionalidade CSS da UI corrigindo problemas com a integração do Tailwind/CDN, conforme descrito no `ROADMAP.md`.

**Arquitetura:** Frontend (SPA) - A correção provavelmente envolverá a inspeção e modificação de arquivos de configuração de build, assets estáticos ou a forma como eles são carregados.

**Tech Stack:** React (presumido com base no `package.json`), Tailwind CSS, PostCSS, CDN.

---

### Tarefa 1: Pesquisar e Diagnosticar o Problema de CSS

**Arquivos:**
- Inspecionar `package.json`
- Inspecionar `tailwind.config.cjs`
- Inspecionar `postcss.config.cjs`
- Inspecionar `index.html` (ou equivalente para carregamento de assets)
- Pesquisar commits recentes relacionados a UI, CSS, Tailwind, CDN.

- [ ] **Passo 1: Identificar a configuração do Tailwind CSS e PostCSS.**
  Ler `tailwind.config.cjs` e `postcss.config.cjs` para entender as configurações atuais e quaisquer mudanças recentes.
  Executar: `read_file(file_path='tailwind.config.cjs')`
  Executar: `read_file(file_path='postcss.config.cjs')`

- [ ] **Passo 2: Verificar como os assets CSS/JS são carregados.**
  Ler `index.html` para verificar se há links de CDN para Tailwind ou outros CSS/JS relacionados à UI.
  Executar: `read_file(file_path='index.html')`

- [ ] **Passo 3: Analisar dependências do frontend.**
  Ler `package.json` para verificar as versões do Tailwind, PostCSS e outros pacotes relacionados, procurando por inconsistências ou dependências desatualizadas.
  Executar: `read_file(file_path='package.json')`

- [ ] **Passo 4: Procurar por commits relevantes.**
  Pesquisar o histórico do Git por commits recentes que envolvam `tailwind`, `css`, `ui`, `assets`, ou `index.html`.
  Executar: `run_shell_command(command='git log --oneline -5 --grep="tailwind\|css\|ui\|assets\|index.html"', description='Pesquisar commits recentes relacionados a UI e CSS.')`

### Tarefa 2: Implementar Correção do Tailwind/CDN

*(Esta tarefa depende da análise da Tarefa 1. Assumindo que a análise revelou um problema com a configuração do Tailwind ou links de CDN, a implementação será a seguinte. O engenheiro precisará ajustar os passos com base nos achados da Tarefa 1.)*

**Arquivos:**
- `tailwind.config.cjs`
- `postcss.config.cjs`
- `index.html`

- [ ] **Passo 1: Aplicar correções na configuração do Tailwind (se necessário).**
  Se a análise indicar um problema com `tailwind.config.cjs`, faça as correções necessárias. Exemplo: Atualizar paths ou plugins.
  *(Este passo é um placeholder. O código exato dependerá da descoberta na Tarefa 1. Um exemplo hipotético seria:*
  ```python
  # Exemplo hipotético:
  # old_string = "content: ['./src/**/*.{js,jsx,ts,tsx}']"
  # new_string = "content: ['./src/**/*.{js,jsx,ts,tsx}', './public/index.html'] # Inclui index.html"
  # execute replace tool
  ```
  *)

- [ ] **Passo 2: Aplicar correções na configuração do PostCSS (se necessário).**
  Se a análise indicar um problema com `postcss.config.cjs`, faça as correções necessárias.
  *(Placeholder para correções no PostCSS.)*

- [ ] **Passo 3: Corrigir links de CDN em `index.html` (se necessário).**
  Se `index.html` estiver com links quebrados ou desatualizados para o Tailwind CSS ou outros assets, corrija-os.
  *(Placeholder para correções no `index.html`.)*

- [ ] **Passo 4: Testar a aplicação.**
  Rodar o comando de build do frontend e verificar se a UI renderiza corretamente sem erros de CSS.
  *(O comando exato para build dependerá do `package.json`. Exemplo comum: `npm run build` ou `yarn build`)*
  Executar: `run_shell_command(command='npm run build', description='Build da aplicação frontend para testar as correções de CSS.')`

- [ ] **Passo 5: Commitar as alterações.**
  Adicionar e commitar os arquivos modificados com uma mensagem clara.
  Executar: `run_shell_command(command='git add . && git commit -m "fix: Ressuscitar CSS com hotfix Tailwind/CDN [STN-UI-01]"', description='Commitar as alterações de correção de CSS.')`

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-10-stn-ui-01-css-hotfix.md`.**

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using `executing-plans`, batch execution with checkpoints

Which approach?