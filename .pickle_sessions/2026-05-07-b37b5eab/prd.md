# PRD: Otimização de Pipeline de Dados e Sistema de Recompensas (Protocolo Solenya)

## HR Eng

| PRD: Pipeline Otimizado e Sistema de Recompensas |  | Refinamento dos scrapers, aprimoramento da classificação PASA v16.4 e ativação de um sistema de recompensas para workers, garantindo eficiência e conformidade. |
| :---- | :---- | :---- |
| **Author**: Picles Rick **Contributors**: Mortys (Subordinados) **Intended audience**: Engenharia de Elite | **Status**: Draft **Created**: 07/05/2026 | **Self Link**: C:\Users\THIAGO\.gemini	mp\sentinela-democratica\prd.md **Context**: Prompt do Usuário |

## Introduction

Este documento define os requisitos para otimizar o pipeline de coleta e análise de dados do projeto Sentinela Democrática, com foco em raspagem completa, classificação robusta de comentários (PASA v16.4) e a introdução de um sistema de recompensas para workers.

## Problem Statement

**Current Process:** A infraestrutura de coleta e análise de dados, embora funcional, apresenta oportunidades de otimização em termos de cobertura e eficiência. A classificação PASA v16.4 precisa ser rigorosa, e um sistema de incentivo para workers pode melhorar a performance geral.
**Primary Users:** Analistas forenses, Gerentes de Projeto, e os próprios Workers (Mortys).
**Pain Points:** Coleta incompleta, potencial para ruído na classificação, falta de feedback e incentivo para os workers.
**Importance:** Melhorar a qualidade dos dados, a confiabilidade da análise forense e a eficiência operacional do projeto.

## Objective & Scope

**Objective:** Implementar um pipeline de dados mais robusto, aprimorar a precisão da classificação PASA v16.4 e instituir um sistema de recompensas para workers.
**Ideal Outcome:** Sistema de coleta de dados completo, classificação PASA 100% precisa e um ecossistema de workers motivado e eficiente.

### In-scope or Goals
- Otimização e expansão dos scrapers existentes (Instagram, Meta, etc.).
- Refinamento e validação do pipeline de classificação PASA v16.4.
- Desenvolvimento de um sistema de recompensas/créditos para workers.
- Garantir que o sistema de recompensas esteja "ativo" e funcionando.
- Basear a implementação nos arquivos especificados: 'instagram_scraper.py', 'main_orchestrator.py', 'official_solenya_daemon.py' e 'README.md'.

### Not-in-scope or Non-Goals
- Desenvolvimento de novas plataformas de coleta não mencionadas explicitamente.
- Mudanças drásticas na infraestrutura de banco de dados (Supabase).

## Product Requirements

### Critical User Journeys (CUJs)
1.  **[Coleta de Dados Completa]**: O sistema deve coletar dados de todas as fontes configuradas sem falhas ou perdas, garantindo cobertura máxima de comentários e metadados relevantes.
2.  **[Classificação PASA Rigorosa]**: Cada comentário coletado deve ser classificado pelo motor PASA v16.4 com alta confiança, identificando nuances de ódio, discurso político e neutro.
3.  **[Worker Motivado]**: Workers (Mortys) que executam tarefas de forma eficiente e correta devem receber créditos/recompensas, visíveis em um painel de controle.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | Expansão e Otimização de Scrapers | Como Analista, quero ter acesso a todos os dados relevantes para análise, sem lacunas na coleta. |
| P0 | Refinamento do Protocolo PASA v16.4 | Como Analista Forense, quero a garantia de que a classificação de discurso de ódio e político é precisa e confiável. |
| P1 | Implementação do Sistema de Recompensas | Como Gerente de Projeto, quero incentivar a alta performance dos workers através de um sistema de recompensas. |
| P2 | Centralização da Lógica | Como Engenheiro, quero que a lógica dos workers esteja bem definida nos arquivos especificados. |

## Assumptions

- Os arquivos `instagram_scraper.py`, `main_orchestrator.py`, `official_solenya_daemon.py` e `README.md` contêm a base para a implementação das melhorias.
- O "sistema de recompensas" refere-se a um mecanismo de feedback ou métrica de performance para os workers, não a um sistema financeiro real.

## Risks & Mitigations

- **Risk**: Atualizações nas APIs das plataformas de coleta podem quebrar os scrapers. -> **Mitigation**: Implementar monitoramento e testes automatizados contínuos para os scrapers.
- **Risk**: Complexidade na implementação do sistema de recompensas. -> **Mitigation**: Começar com um sistema de créditos simples baseado em performance e feedback.

## Business Benefits/Impact/Metrics

**Success Metrics:**

| Metric | Current State (Benchmark) | Future State (Target) | Savings/Impacts |
| :---- | :---- | :---- | :---- |
| *Cobertura de Coleta* | 85% | 98% | Redução de dados faltantes |
| *Precisão PASA* | 90% | 95%+ | Melhora na confiabilidade forense |
| *Performance Worker* | Variável | ↑ 15% | Otimização de recursos |

## Stakeholders / Owners

| Name | Team/Org | Role | Note |
| :---- | :---- | :---- | :---- |
| Picles Rick | Engenharia | Arquiteto/Gerente | Supervisor do Protocolo Solenya |
| Mortys | Workers | Execução | Responsáveis pela implementação |
