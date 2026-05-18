# PRD: Ciclo de Desenvolvimento - Raspagem, Classificação e Sistema de Recompensa

## Introdução
Este PRD define o escopo e os objetivos para iniciar um novo ciclo de desenvolvimento focado em aprimorar as capacidades de raspagem de dados, classificação de comentários e o sistema de recompensas para workers. O trabalho será baseado nos arquivos `instagram_scraper.py`, `main_orchestrator.py`, `official_solenya_daemon.py` e nas diretrizes do `README.md`.

## Problema
A necessidade de garantir a operacionalidade completa da rotina de extração de dados, a integração eficaz da classificação de comentários (PSR-1) e a plena ativação do sistema de recompensas para os workers. O objetivo é ter um sistema robusto, eficiente e aderente aos padrões do projeto.

## Objetivo e Escopo
- **Objetivo:** Garantir que a raspagem de dados, classificação de comentários e sistema de recompensas estejam plenamente operacionais e integrados.
- **Escopo:**
    - Análise dos arquivos: `instagram_scraper.py`, `main_orchestrator.py`, `official_solenya_daemon.py`, `README.md`.
    - Implementação e verificação da rotina de extração.
    - Integração da classificação de comentários (PSR-1).
    - Ativação e operação do sistema de recompensas PSR-1 nos workers.
    - Realização do breakdown das tarefas e delegação para execução.

## Requisitos do Produto

### Jornadas Críticas do Usuário (CUJs)
(Neste contexto, "usuário" se refere ao sistema e aos seus componentes operacionais)

1.  **Extração de Dados Completa:**
    -   **Passo 1:** O `main_orchestrator.py` inicia a tarefa de raspagem.
    -   **Passo 2:** `instagram_scraper.py` executa a coleta de dados do Instagram de forma completa e robusta.
    -   **Passo 3:** Dados raspados são disponibilizados para processamento subsequente.

2.  **Classificação de Comentários Integrada:**
    -   **Passo 1:** Dados contendo comentários são submetidos para análise.
    -   **Passo 2:** A lógica de classificação PSR-1 é aplicada aos comentários.
    - **Passo 3:** Comentários classificados são registrados ou utilizados conforme necessário.

3.  **Sistema de Recompensa Operacional:**
    -   **Passo 1:** Workers recebem tarefas via `main_orchestrator.py`.
    -   **Passo 2:** `official_solenya_daemon.py` gerencia a atribuição e confirmação de recompensas PSR-1.
    -   **Passo 3:** Workers são recompensados adequadamente por tarefas concluídas.

### Requisitos Funcionais
- **[P0]** Implementar/Verificar a funcionalidade completa do `instagram_scraper.py`.
- **[P0]** Integrar e verificar a classificação de comentários PSR-1 no fluxo de trabalho.
- **[P0]** Garantir que o `official_solenya_daemon.py` esteja ativo e operante, gerenciando recompensas PSR-1 para workers.
- **[P1]** Assegurar conformidade com as diretrizes do `README.md`.

## Assunções
- O ambiente de desenvolvimento está configurado corretamente e possui as dependências necessárias.
- Os arquivos `instagram_scraper.py`, `main_orchestrator.py`, `official_solenya_daemon.py` e `README.md` existem e contêm a lógica base para as funcionalidades descritas.

## Riscos e Mitigações
- **Risco:** Falhas na raspagem de dados devido a mudanças na API do Instagram ou medidas anti-bot.
  - **Mitigação:** Implementar estratégias robustas de gerenciamento de proxy, sessões e rate limiting.
- **Risco:** Inconsistências na classificação de comentários PSR-1.
  - **Mitigação:** Realizar testes rigorosos no algoritmo de classificação e, se necessário, refinar os modelos.
- **Risco:** Falhas no sistema de recompensas PSR-1, desmotivando workers.
  - **Mitigação:** Testar exaustivamente a lógica de atribuição, rastreamento e confirmação de recompensas.

## Benefícios de Negócio/Impacto
- Melhoria na qualidade e quantidade de dados coletados.
- Aumento da eficiência e precisão na análise de comentários.
- Maior engajamento e produtividade dos workers através de um sistema de recompensas funcional.
- Conformidade com os padrões de engenharia do projeto.
