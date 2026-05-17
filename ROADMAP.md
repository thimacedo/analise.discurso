# 🗺️ ROADMAP.md - Sentinela Democrática

## ✅ Concluído (PASA v17 - v47.10)

### Fundação e Core (v17 - v24)
- [x] Arquitetura BaseWorker com Event Bus e Gamificação (XP/Level).
- [x] Circuit Breaker para proteção de sessão e fila.
- [x] Rota de Injeção de Sessão de Emergência (Instagram Cookies).
- [x] Cache Busting e integração Stripe no Frontend.

### Fortaleza Instagram e Fila (v25 - v34)
- [x] Quality Gate v2 (Filtro rigoroso de lixo de UI do scraper).
- [x] Integração do SDK `google-genai` e processamento em massa.
- [x] Raspagem de Longo Curso com delays humanos (Anti-ban).
- [x] Fila Inteligente com Cooldown de 6h (Evita perfis repetidos).

### Inteligência e Convergência (v35 - v44)
- [x] Nó Local (War Room) com Watchdog Guardião e Auto-cura.
- [x] Monitor de Ameaças ao Vivo (Git Sync JSON -> Vercel).
- [x] Descanso Produtivo (IA trabalha enquanto scraper hiberna).
- [x] MCA v2.2 (Manual de Classificação Analítica) com CCF e Direção de Risco mapeada.
- [x] Proteção Jurídica e Acadêmica (Remoção de termos forenses, criação da MSAL).
- [x] Auditoria Cruzada Anti-Alucinação (Groq/Llama 3) e Métricas de Deriva.

### Governança e Otimização Serverless (v45 - v47.10)
- [x] Interface Web para gerenciamento de `scraping_accounts` (Sessões).
- [x] Otimização de bundle size do Vercel (<300MB) para backend Python.
- [x] Sistema de monitoramento de saúde de workers (`workers_metrics`).
- [x] Backend refatorado para compatibilidade total com Vercel Serverless.
- [x] Rotação automática de contas de scraping configurável via UI.

---

## 🚀 Próximos Passos (Backlog)

### Migração Frontend: O Salto para Bleeding Edge (Prioridade Máxima)
- [ ] **Fase 1: Setup Híbrido** - Next.js (App Router), Tailwind v4, Shadcn na raiz, roteando `/api` para o FastAPI via Vercel.
- [ ] **Fase 2: The God Mode Data Layer** - Conexão nativa SSR via `@supabase/supabase-js` com React Query e Zustand. Sem ORMs lixo.
- [ ] **Fase 3: UI & Dashboards** - Componentização profissional ("War Room"), migrando gráficos para Recharts.
- [ ] **Fase 4: Expurgo do Legado** - Deleção do Vanilla JS antigo (`app.js`, `index.html`) e finalização do deploy Vercel unificado.

### Maestria Instagram (v48+)
- [ ] Expansão de escopo: Raspagem de Reels, Stories e comentários em threads encadeadas.
- [ ] Mapeamento de shadowbans: Detectar quando o alvo esconde comentários automaticamente.
- [ ] Análise de engajamento: Correlacionar número de likes com a severidade do discurso.

### Refinamento de Dados
- [ ] Dashboard de Auditoria Humana para revisão de `audit_discrepancy = True`.
- [ ] Exportação de Relatórios em PDF (Indícios de Risco) para stakeholders.
- [ ] Mapeamento de redes coordenadas com grafos interativos no frontend.

### Refinamento de IA
- [ ] Few-shot dinâmico baseado no `audit_gold_standards` (Padrão Ouro).
- [ ] Fine-tuning de modelo leve local (Ollama) para reduzir dependência de API.
