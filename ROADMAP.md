# ROADMAP DETALHADO - Sentinela Democrática

Este documento define a estratégia, o progresso e os planos de ação do projeto Sentinela Democrática, seguindo uma abordagem de planejamento real e detalhada.

## Visão Geral do Projeto
O Sentinela Democrática visa ser uma plataforma robusta para coleta, análise e visualização de dados de discurso de ódio e tendências políticas, com foco em inteligência forense e conformidade com o Protocolo PASA v16.4. A arquitetura busca integrar frontend, backend e capacidades de IA de forma escalável e auditável.

---

## Fase 1: Fundação e Infraestrutura Essencial (NOW)

### Épico: STN-001 - Infraestrutura de Dossiês Forenses (Persistência em Banco de Dados)
*   **Status:** Plano Rascunhado (Implementação Bloqueada por Ferramentas)
*   **Objetivo:** Substituir armazenamento de PDF por banco SQLite.
*   **Componentes Principais:** Criação de `data/database.py` (schema SQLite), modificação em `processing/dossie_service.py`.
*   **Dependências:** N/A (local).
*   **Foco:** Estabelecer a base de dados para os relatórios forenses.

### Épico: Integração de Analytics (Google Analytics & Vercel)
*   **Status:** Backlog (requer definição de escopo e páginas afetadas)
*   **Objetivo:** Monitorar uso e performance do sistema.
*   **Componentes Principais:** Frontend (HTMLs: `index.html`, `analise.html`, `metodo.html`, `docs/analise-violencia.html`, etc.), configuração do Google Analytics (GA4).
*   **Foco:** Visibilidade de uso e performance do produto.

---

## Fase 2: Desenvolvimento do Motor de Inteligência (SOON)

### Épico: STN-003 - Integração Meta Ad Library (ACTIVE)
*   **Status:** Ticket Breakdown Concluído (Local).
*   **Objetivo:** Capturar anúncios financiados para identificar fluxos de desinformação paga.
*   **Componentes Principais:** `core/meta_ad_service.py`, Schema de banco `meta_ads`, Integração com `AIService` (PASA).
*   **Foco:** Monitoramento proativo de financiamento político.

### Épico: STN-002 - Motor de Inteligência PASA v16.4
*   **Status:** Pesquisa Concluída (aguardando definição externa da lógica PASA); Pesquisa e Revisão documentadas internamente.
*   **Objetivo:** Integrar regras PASA v16.4 ao pipeline de processamento.
*   **Componentes Principais:** Módulo PASA (e.g., `core/pasa_logic.py`), modificação em `processing/text_processor.py`.
*   **Foco:** Aprimorar a precisão e conformidade da classificação de conteúdo.

### Épico: Diretório Global de Perfis
*   **Status:** Backlog
*   **Objetivo:** Criar tabela unificada de alvos com histórico de comportamento forense.
*   **Componentes Principais:** Modelagem de dados, backend para gerenciamento de perfis.

---

## Fase 3: Expansão e Visualização (LATER)

### Épico: Mapa Geopolítico UF
*   **Status:** Backlog
*   **Objetivo:** Desenvolver frontend para visualização integrada de dados políticos por Unidade Federativa (UF).
*   **Componentes Principais:** Frontend interativo, integração com dados de backend.

---

## Fase 4: Escalabilidade e Otimização (LONG TERM)

### Épico: Implementar Filas (Celery/Redis)
*   **Status:** Long Term
*   **Objetivo:** Melhorar a capacidade de processamento para alto volume de dados.

### Épico: Avaliar Upgrade Ollama
*   **Status:** Long Term
*   **Objetivo:** Explorar modelos de IA com maior capacidade para análise.

---

## Concluído (COMPLETED)

*   [**Monitoramento de Monetização**]: Injeção de AdSense validada.
*   [**Diamond Stability v20.5.1**]: Frontend blindado, Ollama unificado e monetização injetada.
