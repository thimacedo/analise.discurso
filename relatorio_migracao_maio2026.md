# 📝 RELATÓRIO DE EXECUÇÃO: MIGRAÇÃO E MAESTRIA (MAIO 2026)

## 1. Resumo das Execuções (Autônomas)
- **Frontend Modernizado:** Migração do stack de `Vanilla JS` para `Next.js 16 (App Router) + Tailwind v4 + Shadcn UI + Zustand`, garantindo SSR e um design system tático (“War Room”).
- **Infraestrutura:** Integração nativa com `@supabase/supabase-js` e `TanStack Query`, eliminando camadas legadas e simplificando a orquestração de dados.
- **Maestria Instagram:** Implementada detecção forense de *shadowban* (flags `comments_enabled`, `shadowban_likely`) no motor `scraper_headless.py` e fallback por tiers.
- **Observabilidade:** Watchdog com SSE corrigido (`Content-Type: text/event-stream`), logs estruturados e captura de stdout/stderr em tempo real.
- **Governança:** Commits atômicos (`feat`/`chore`/`fix`) com push imediato e revisão de PRs curtos.

## 2. Status Atual do Ecossistema
- **Arquitetura:** `PASA v50.0` (Watchdog v50.0 operacional).
- **Frontend:** Operacional (build validado no App Router).
- **Backends/Scrapers:** Tiers integrados. Tier 4 (Playwright) funcional; Tier 3 (Zyte) com heurística para abortar em login wall; Tier 1/2 com validação em andamento.
- **Dados:** Operação real ativada (Zero Mocks). Persistência via Supabase normalizada.

## 3. Evidências e KPIs (Mínimo Viável)
- **Taxa de sucesso por Tier (últimas 24h):**
  - T1 API: — (em validação)
  - T2 DOM: — (em validação)
  - T3 Zyte: % sucesso, % login wall
  - T4 Headless: % sucesso
- **Tempo médio por coleta (p95):** alvo → comentários (s)
- **Erros notáveis:** HTTP 429 (contagem), PGRST 204 (schema cache), timeouts por Tier
- **Custo (Zyte):** requisições/dia
- **Persistência:** inserts OK/KO (com motivo) por janela de 24h

## 4. Migrações e Operações no Supabase (Maio/2026)
- **Colunas adicionadas:** `post_shortcode` TEXT, `tier_used` INTEGER, `like_count` INTEGER.
- **Ação operacional necessária pós-DDL:**
  - `NOTIFY pgrst, 'reload schema';`
  - Validação: `GET /rest/v1/comentarios?select=post_shortcode&limit=0` deve retornar 200.
- **Mapeamento de persistência padronizado:** `id_externo`, `candidato_id`, `post_shortcode`, `autor_username`, `texto_bruto`, `data_publicacao`, `data_coleta`, `likes`, `tier_used`.

## 5. Runbook de Incidentes (sumário)
- **SSE “application/json” em /api/stream:** Corrigido para `text/event-stream` + keepalive.
- **429 generalizado no Instagram:** Fallback automático de T1/T2 para T3/T4; aplicar delays e cabeçalhos realistas.
- **PGRST204 (schema cache):** `NOTIFY pgrst, 'reload schema';` + headers `Content-Profile`/`Accept-Profile: public`.
- **Zyte:** Abortar cedo ao detectar login wall para economizar créditos.

## 6. Próximos Passos (Backlog Estratégico)

### A. Refinamento de Interface (Bleeding Edge)
- [ ] Construir 6 abas restantes do painel (Análise Forense, Alvos, Dossiês, Alertas, Rede, Fila).
- [ ] Gráficos interativos (Recharts) para clusters e correlações.

### B. Dados e Inteligência
- [ ] Dashboard de latência e taxa de sucesso por Tier (24h/7d).
- [ ] Integrar flags de shadowban/comments_enabled à persistência e UI (filtros).
- [ ] Correlação likes x severidade de discurso (PoC com amostra estratificada).

### C. Confiabilidade e Custos
- [ ] Hardening do Tier 1/2: runner no diretório `sentinela_scrapy`; Playwright somente no Tier 2 via `custom_settings`; retry e backoff por 429.
- [ ] Guard rails do Zyte: limites por ciclo, logs de custo básico.
- [ ] Healthcheck Supabase + reload schema automatizado em deploy.

### D. Governança e Segurança
- [ ] Auditoria de RLS (Next.js não deve exfiltrar dados sensíveis).
- [ ] Gestão de segredos (SessionID, chaves Zyte) com rotação e escopo mínimo.
- [ ] Documentação de arquitetura atualizada (`architecture_map.md`).
