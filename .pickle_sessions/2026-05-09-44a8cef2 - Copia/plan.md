# Plano de Implementação - Milestone v20.6 (Estabilização)

> **Para agentes:** REQUISITO SUB-SKILL: Use superpowers:subagent-driven-development para implementar este plano tarefa por tarefa.

**Objetivo:** Blindar o frontend contra falhas de API, otimizar memória e corrigir monetização.

---

### Fase 1: Resiliência e Null-Safety (STN-001)

**Arquivos:** `src/core/app.js`, `src/core/ui.js`

- [ ] **Passo 1: Blindagem de `refreshData`**
  No `app.js`, envolver a atribuição de `state.summary` em um bloco mais seguro e garantir que `renderAll` receba fallbacks.
  ```javascript
  // src/core/app.js
  renderAll(summary || {}, targets || [], alerts || []);
  ```
- [ ] **Passo 2: Optional Chaining em `ui.js`**
  Garantir que todas as propriedades acessadas em `buildPostCard` usem `?.`.

---

### Fase 2: Otimização de Memória (STN-002)

**Arquivos:** `src/services/dataService.js`, `src/core/app.js`

- [ ] **Passo 1: Limitação de `getTargets`**
  Alterar o limite padrão de 50 para 20 no `dataService.js`.
- [ ] **Passo 2: Injeção Batch no DOM**
  Refatorar `renderFeed` para não usar uma única string gigante via `.join('')`.

---

### Fase 3: Monetização e Cache (STN-003, STN-004)

**Arquivos:** `index.html`, `vercel.json`

- [ ] **Passo 1: Cache Control no Vercel**
  Adicionar a seção de `headers` no `vercel.json`.
- [ ] **Passo 2: IDs Reais**
  Substituir `SIDEBAR_DIAMOND` pelo ID real `7827611269`.

---

### Fase 4: Verificação

- [ ] **Passo 1: Teste de API Offline**
  Parar o backend e verificar se o frontend exibe o "Empty State" sem crashar.
- [ ] **Passo 2: Monitoramento de Memória**
  Abrir o Chrome DevTools > Memory e verificar a Heap após múltiplos scrolls.

---

### Fase 5: Ruthless Refactor - Purga de Workers (STN-006)

**Arquivos:** `api/index.py`, `core/`, `ROADMAP.md`

- [ ] **Passo 1: Inventário de Zombies**
  Listar todos os arquivos na pasta `core/` e verificar quais estão sendo realmente chamados pela API ou pelo `BaseWorker`.
- [ ] **Passo 2: Consolidação**
  Mover lógica dispersa de "Triagem" para um único worker unificado.
- [ ] **Passo 3: A Purga**
  Deletar os arquivos mortos e remover as referências no `ROADMAP.md`.
