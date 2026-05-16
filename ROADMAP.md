# 🗺️ ROADMAP.md - Sentinela Democrática

## ✅ Concluído (PASA v17 - v44)

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

---

## 🚀 Próximos Passos (Backlog)

### Maestria Instagram (v45+)
- [ ] Expansão de escopo: Raspagem de Reels, Stories e comentários em threads encadeadas.
- [ ] Mapeamento de shadowbans: Detectar quando o alvo esconde comentários automaticamente.
- [ ] Otimização de sessão: Rotação automática de contas de scraping para evitar bloqueios humanos.
- [ ] Análise de engajamento: Correlacionar número de likes com a severidade do discurso.

### Governança de Dados
- [ ] Interface Web para gerenciamento de `scraping_accounts` (Sessões).
- [ ] Dashboard de Auditoria Humana para revisão de `audit_discrepancy = True`.
- [ ] Exportação de Relatórios em PDF (Indícios de Risco) para stakeholders.

### Refinamento de IA
- [ ] Few-shot dinâmico baseado no `audit_gold_standards` (Padrão Ouro).
- [ ] Fine-tuning de modelo leve local (Ollama) para reduzir dependência de API.
