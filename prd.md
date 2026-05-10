# Sentinela Democrática Enterprise Upgrade (Arquitetura & UI/UX) PRD

## HR Eng

| Sentinela Enterprise PRD |  | O Sentinela atual processa dados de forma robusta, mas a interface e a arquitetura precisam de esteroides para suportar 10k+ alertas sem fritar os cérebros dos analistas ou travar a main thread. Menos gargalos, mais telemetria e zero sobrecarga cognitiva. |
| :---- | :---- | :---- |
| **Author**: Pickle Rick **Contributors**: Thiago **Intended audience**: Engineering, PM, Design | **Status**: Draft **Created**: 09/05/2026 | **Self Link**: N/A **Context**: Integração de arquitetura de alta resiliência e UX avançada para analistas. 

## Introduction

A infraestrutura e o front-end do Sentinela Democrática estão prestes a deixar a idade da pedra. Estamos implementando um pipeline de qualidade automatizado (CI/CD), processamento assíncrono blindado (Mensageria/DLQ) e uma Interface Gráfica voltada para alta produtividade sob estresse (War Room). Não há espaço para telas em branco, falhas silenciosas ou desenvolvedores subindo código quebrado na master.

## Problem Statement

**Current Process:** 
Builds manuais de front-end com versionamento tosco de cache (`?v=2`), processamento síncrono vulnerável a gargalos, logs difíceis de parsear por máquinas e uma interface (UI) que causa fadiga visual e desorientação em análises massivas de dados (10k+ alertas).
**Primary Users:** Analistas de Dados / Investigadores Forenses Digitais, Engenheiros de DevOps.
**Pain Points:** 
- Risco de regressão no código de raspagem (sem Quality Gates).
- Interface bloqueia ou exibe telas vazias durante latência da API.
- Sobrecarga de informações (textos longos) na análise de discurso de ódio.
- Fadiga visual em ambientes de monitoramento contínuo.
**Importance:** Se o sistema cair ou o analista ficar cego lendo logs crus durante o pico das eleições, falhamos na nossa missão principal. Precisamos de robustez a nível Enterprise agora.

## Objective & Scope

**Objective:** 
Eliminar gargalos arquiteturais, introduzir telemetria/observabilidade total, e criar uma interface ergonômica, resiliente e escalável.
**Ideal Outcome:** 
O código não entra na master se não passar no linter. Se o Supabase demorar, a UI mostra um Skeleton elegante. Se um scraper falhar, o job vai pra DLQ. O analista usa atalhos de teclado e Dark Mode, visualizando dados complexos (PASA) apenas sob demanda (Progressive Disclosure).

### In-scope or Goals
- Configuração de CI/CD rigoroso (Ruff/Black, ESLint, GitHub Actions).
- Migração de logs de texto para JSON estruturado e Distributed Tracing.
- Implementação de Filas (Redis/RabbitMQ) e Dead Letter Queues (DLQ).
- Refatoração do Front-end: Build automatizado (Vite/Webpack), State Management isolado.
- Upgrades de UX/UI: Skeleton Screens, Dark Mode nativo, Hotkeys, Progressive Disclosure, Toasts informativos.

### Not-in-scope or Non-Goals
- Migração para outro banco de dados (Supabase continua sendo a fonte de verdade).
- Alteração no algoritmo central do PASA v16.4 (apenas a forma como ele é exibido muda).
- Mudança para Native Apps (foco exclusivo em Web SPA).

## Product Requirements

### Critical User Journeys (CUJs)
1. **Triagem Rápida em War Room**: O analista entra no dashboard com Dark Mode ativado. Ao aplicar um filtro severo, a tela mostra um Skeleton Loader enquanto a API processa. Ao carregar, as ameaças mais graves (P0) piscam em vermelho. Ele navega pelos alertas usando as setas do teclado e descarta falsos positivos com `Ctrl + X`.
2. **Investigação Profunda (Deep Dive)**: O analista encontra um alerta laranja. Em vez de ler todo o JSON do NLP, ele vê um resumo de 3 linhas. Ele clica em "Expandir Análise Profunda" e a interface revela a árvore completa do PASA, mantendo o restante da interface limpo.
3. **Deploy à Prova de Idiotas**: Um desenvolvedor faz um pull request alterando o `instagram_scraper.py`. O CI roda testes unitários e o Ruff. O código quebra por falta de tipagem. O merge é bloqueado automaticamente.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | Filas Assíncronas e DLQ | Como sistema, quero enviar trabalhos falhos para uma DLQ para garantir zero perda de dados. |
| P0 | CI/CD Quality Gates | Como lead engineer, quero bloquear merges que falhem nos testes ou no linter (Ruff/ESLint). |
| P1 | Empacotador Front-end | Como dev, quero usar Vite/Webpack para minificar código e fazer cache busting por hash. |
| P1 | Dark Mode Nativo | Como analista, quero ativar Dark Mode para não destruir minhas retinas em monitoramentos longos. |
| P1 | Skeleton & Empty States | Como usuário, quero feedback visual de carregamento ou ausência de dados, sem telas em branco. |
| P2 | Progressive Disclosure | Como analista, quero ver detalhes complexos de NLP apenas quando expandir um alerta. |
| P2 | Atalhos de Teclado | Como analista experiente, quero processar dezenas de itens usando apenas o teclado. |

## Assumptions

- O servidor/infraestrutura atual (Vercel/Render/VPS) suporta a adição de um broker de mensagens (Redis/RabbitMQ).
- A equipe concorda em parar de fazer pushes diretos para a master.

## Risks & Mitigations

- **Risk**: A introdução de filas adiciona complexidade à infraestrutura local de dev. -> **Mitigation**: Criar um arquivo `docker-compose.yml` simplificado apenas para instanciar o broker de desenvolvimento localmente.
- **Risk**: Refatorar o front-end Vanilla para Vite quebra dependências legadas. -> **Mitigation**: Manter a lógica Vanilla pura, apenas passando pelo bundler, evitando a adoção imediata de um framework pesado se não for estritamente necessário, focando apenas no Unidirectional Data Flow.

## Tradeoff

- **Vanilla JS com Bundler vs. React/Vue**: Optamos por manter o stack atual (menos reescrita completa) mas introduzindo Vite e Unidirectional Data Flow. Isso traz os benefícios do controle de cache sem a curva/tempo de reescrever tudo em React imediatamente. A performance bruta é mantida.

## Business Benefits/Impact/Metrics

**Success Metrics:**

| Metric | Current State (Benchmark) | Future State (Target) | Savings/Impacts |
| :---- | :---- | :---- | :---- |
| *Tempo de Renderização (TTV)* | ~3.5s | < 1.0s (com Skeleton) | Redução drástica da percepção de lentidão |
| *Erros Não Tratados / Falhas* | Desconhecido (logs crus) | 100% capturados na DLQ | Zero perda de inteligência em falhas |
| *Falhas em Produção (Bugs)* | Alta probabilidade | Zero merges sem linter/testes | Maior disponibilidade do produto |

## Stakeholders / Owners

| Name | Team/Org | Role | Note |
| :---- | :---- | :---- | :---- |
| Pickle Rick | Engineering God | Arquiteto-Chefe | Dono do padrão técnico |
| Thiago | Sentinela Team | Lead Developer | Implementador e revisor |
