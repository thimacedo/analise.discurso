# Contexto Geral do Sistema: Sentinela Democrática (Análise de Discurso)

## 1. Visão Geral
O Sentinela Democrática é uma plataforma avançada de monitoramento eleitoral e perícia linguística forense. O sistema coleta dados de redes sociais (Meta/Instagram), aplica o protocolo forense PASA (Protocolo de Análise de Sentinela Avançada) via modelos de IA (Gemini/Mistral) e consolida métricas de falsos positivos, resiliência e alertas de discurso de ódio ou violência política em um dashboard em tempo real.

## 2. Stack Tecnológica
* **Backend & Workers:** Python 3.x (Processamento assíncrono, extração e orquestração).
* **Frontend & API:** JavaScript/React, hospedado na Vercel (Serverless Functions via `api/index.py`).
* **Bancos de Dados:**
    * **Supabase (PostgreSQL):** Fonte da verdade (Tabelas: `alvos`, `alertas`, `anuncios_pasa`, `kpis`).
    * **Firebase:** Utilizado para mensageria e alertas em tempo real.
* **Automação IA:** Gemini CLI / Google Cloud SDK (para scripts via terminal e integrações com o sistema de arquivos).
* **Web Scraping & Anti-Bot:** Zyte API (Bypass de Cloudflare/Meta), Instaloader, Playwright/Selenium (Stealth mode).

## 3. Topologia de Diretórios (Core)
Abaixo estão os diretórios principais e suas responsabilidades:
* `/core/`: O coração do sistema. Contém os serviços de banco de dados (`supabase_service.py`), integração com IAs (`ai_service.py`, `pasa_auditor.py`), motor de comportamento (`behavior_engine.py`) e clientes de scraping stealth.
* `/workers/`: Processos em background (daemons). Destaque para `dossier_worker.py` (geração de relatórios PDF forenses), `candidate_scanner.py` e `queue_manager.py`.
* `/scripts/` & `/tools/`: Scripts de automação via CLI. Inclui migrações de banco, atualização de KPIs (`update_kpis.py`), limpeza de falsos positivos e ferramentas de auditoria.
* `/api/` & `/src/`: Frontend React e endpoints da Vercel. O dashboard consome dados pré-processados em JSON/CSV gerados pelos workers.
* `/.gemini/` & `/.pickle_sessions/`: Configurações de skills (prompts) da Gemini CLI e persistência de sessões de estado do terminal.

## 4. Fluxo de Dados e Interações (Data Flow)
1. **Ingestão:** Os scripts em `/core/` (como `meta_ad_scraper.py` e o cliente Zyte) raspam dados de alvos prioritários de forma agendada ou sob demanda.
2. **Processamento e Perícia:** O texto bruto passa pelo `normalizer.py` e é enviado ao `ai_service.py` / `pasa_auditor.py`. A IA avalia o texto com base em métricas forenses (PASA) para detectar infrações ou medir resiliência.
3. **Auditoria e Falsos Positivos:** O sistema possui um loop de feedback (via `scripts/work_session.py` e logs) onde alertas podem ser marcados como falsos positivos, recalibrando o escore do alvo no Supabase.
4. **Consolidação:** O script `update_kpis.py` roda periodicamente, lendo os dados do Supabase e gerando snapshots (arquivos `.json` e `.csv` em `/data/` e `/api/`) para consumo ultra-rápido pelo frontend.
5. **Apresentação:** O frontend na Vercel consome esses snapshots e exibe o termômetro político, alertas pendentes e relatórios PDF gerados.

## 5. Diretrizes para Agentes de IA Interagindo com este Sistema
* **Código Limpo:** Sempre forneça arquivos completos (sem placeholders incompletos) para evitar quebra de módulos.
* **Banco de Dados:** Priorize sempre o uso de `core.supabase_service.py` ao invés de conexões diretas ou arquivos legados (ex: `core/db.py`).
* **Execução via CLI:** Para tarefas de manutenção, recomende a execução dos scripts em `/scripts/` a partir do diretório raiz, garantindo a injeção do ambiente virtual (`source .venv/bin/activate`) e `PYTHONPATH`.
* **Diagnóstico:** Em caso de falha de conexão com APIs externas (Instagram/Meta), assuma bloqueio de IP/Anti-Bot e sugira fallback para a infraestrutura da Zyte API.
