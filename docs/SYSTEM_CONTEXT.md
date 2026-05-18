# Contexto Geral do Sistema: Sentinela Democrática (Análise de Discurso)

## 1. Visão Geral
O Sentinela Democrática é uma plataforma avançada de monitoramento eleitoral e perícia linguística forense. O sistema coleta dados de redes sociais (Meta/Instagram), aplica o protocolo forense PASA (Protocolo de Análise de Sentinela Avançada) via modelos de IA (Gemini/Mistral) e consolida métricas de falsos positivos, resiliência e alertas de discurso de ódio ou violência política em um dashboard em tempo real.

## 2. Stack Tecnológica
* **Backend & Workers:** Python 3.x (Processamento assíncrono, extração e orquestração).
* **Frontend & API:** Next.js (App Router), Tailwind v4, Shadcn UI + Supabase Client, hospedado na Vercel.
* **Bancos de Dados:** 
    * **Supabase (PostgreSQL):** Fonte da verdade (Ingestão de comentários, perfis, KPIs).
* **Automação IA:** Gemini CLI / Google Cloud SDK / Groq.
* **Web Scraping & Anti-Bot (Engine PASA v49.9+):** 
    * **Motor Principal:** Zyte API (Bypass de Cloudflare/Meta via JSON API, Browser Rendering, e Proxy Mode).
    * **Fallback:** Playwright (`scraper_headless.py`) em modo stealth.

## 3. Topologia de Diretórios (Core)
* `/core/`: Serviços de banco (`supabase_service.py`), IA (`ai_service.py`), motor de comportamento (`behavior_engine.py`), e o checker de saúde (`zyte_checker.py`).
* `/app/workers/`: Onde reside o `InstagramWorker` (orquestrador de coleta).
* `/scripts/`: Automação de manutenção, migrações SQL, e ferramentas de auditoria.
* `/docs/`: Documentação técnica e de conformidade.
* `/supabase/migrations/`: Histórico de evolução do esquema SQL.
* `/frontend-bleeding-edge/`: Novo frontend Next.js em migração.

## 4. Fluxo de Dados (Zyte-Driven Pipeline)
1. **Orquestração:** `local_server.py` gerencia o loop de coleta, respeitando cooldowns.
2. **Ingestão (Zyte):** `InstagramWorker` solicita dados ao `scraper_zyte.py`, que utiliza estratégia tripla (API JSON -> Renderização Browser -> DOM Regex).
3. **Resiliência:** O `watchdog.py` monitora o status do servidor e a saúde da API Zyte, disparando alertas via WhatsApp (CallMeBot) em caso de falha.
4. **Persistência:** Sanitização via `InstagramWorker` -> `supabase.table('comentarios').upsert(...)`.

## 5. Regras de Negócio (Compliance & Créditos)
* **Distribuição Igualitária:** Cooldown de 12 horas por perfil. Apenas 3 alvos por ciclo de raspagem (a cada 30 min) para economizar créditos Zyte e evitar bans.
* **Elite Política (Prioridade 10):** 29 perfis (Presidenciáveis, Governadores, Lideranças Nacionais) possuem prioridade máxima de coleta.
* **Compliance Legal:** Perfis da família Bolsonaro (com exceção de Eduardo/Carlos) possuem `status_monitoramento` pausado por restrições legais.
* **Auto-Auditoria:** Falhas de username (erro 404) são logadas automaticamente em `divergent_usernames.log`.

## 6. Status de Desenvolvimento e Roadmap
* **Migração Frontend:** Fase 1 (Setup Híbrido - Next.js/Tailwind) Concluída. Iniciando Fase 2 (Data Layer God Mode).
* **Pipeline de Coleta:** Operacional com Zyte X-Engine.
* **Prioridade:** Elite Política (29 Alvos) e Monitoramento de Saúde (Watchdog).

## 7. Diretrizes para Agentes de IA
* **Segurança:** Nunca execute comandos que exponham chaves de API (`.env`).
* **Supabase:** Utilize sempre o padrão de migrações (`/supabase/migrations/`) para alterações de schema.
* **Configuração:** Ao realizar mudanças no fluxo de coleta, sempre documente a alteração em `MEMORY.md`.
