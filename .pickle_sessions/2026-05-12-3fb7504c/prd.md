# Consolidação e Limpeza de Tickets do Projeto Sentinela PRD

## HR Eng

| Consolidação e Limpeza de Tickets PRD |  | Auditoria e purga de tickets legados para centralizar o backlog e limpar o repositório de arquivos obsoletos. |
| :---- | :---- | :---- |
| **Author**: Pickle Rick **Contributors**: Morty **Intended audience**: Engineering | **Status**: Draft **Created**: 12/05/2026 | **Self Link**: N/A **Context**: Limpeza de slop de gerenciamento |

## Introduction

O projeto Sentinela acumulou diversos arquivos de tickets (.md) ao longo do tempo. Muitos estão finalizados, outros duplicados ou obsoletos. Este PRD visa automatizar a varredura, consolidação e remoção desses arquivos.

## Problem Statement

**Current Process:** Tickets são espalhados pelo repositório em arquivos como linear_ticket_*.md, PENDING_TICKETS.md, etc.
**Primary Users:** Engenheiros (Rick) e estagiários confusos (Morty).
**Pain Points:** Poluição visual do repositório, dificuldade em rastrear o progresso real, risco de trabalhar em tarefas obsoletas.
**Importance:** Essencial para manter o projeto "Solenya-tight" e evitar confusão técnica.

## Objective & Scope

**Objective:** Centralizar tarefas pendentes e eliminar arquivos de tickets legados.
**Ideal Outcome:** Um repositório limpo com apenas um backlog mestre consolidado.

### In-scope ou Goals
- Varredura recursiva de arquivos de ticket (*.md).
- Classificação de status (Done vs Pending).
- Criação de CONSOLIDATED_BACKLOG.md.
- Exclusão segura dos arquivos legados processados.

### Not-in-scope ou Non-Goals
- Não vamos refatorar o código mencionado nos tickets, apenas gerenciar os documentos de rastreamento.

## Product Requirements

### Critical User Journeys (CUJs)
1. **Auditoria de Tickets**: O sistema identifica todos os arquivos que parecem tickets, lê seu conteúdo e extrai descrições de tarefas e status.
2. **Consolidação de Backlog**: O sistema gera um novo arquivo contendo todas as tarefas que ainda não foram marcadas como finalizadas.
3. **Purga de Legado**: Após a consolidação, todos os arquivos de tickets antigos identificados são deletados permanentemente.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | Identificação de arquivos de ticket | Como Rick, quero que o sistema ache todo ticket perdido no repo. |
| P0 | Extração de tarefas pendentes | Como Rick, quero saber o que ainda falta fazer sem ler 20 arquivos. |
| P0 | Geração de Backlog Consolidado | Como Rick, quero um único arquivo mestre de tarefas. |
| P1 | Exclusão de arquivos processados | Como Rick, quero deletar a sujeira do meu repo. |

## Assumptions

- Arquivos que começam com linear_ticket_ ou estão em pastas de tickets são alvos válidos.
- Tarefas marcadas com [x] ou status: Done são consideradas finalizadas.

## Risks & Mitigations

- **Risk**: Deletar um ticket que tinha informações importantes não capturadas. -> **Mitigation**: Fazer um dump completo do conteúdo pendente no novo backlog antes de deletar.

## Tradeoff

- Optamos por um único arquivo mestre em vez de manter a estrutura de pastas para facilitar a visibilidade imediata.

## Business Benefits/Impact/Metrics

**Success Metrics:**

| Metric | Current State (Benchmark) | Future State (Target) | Savings/Impacts |
| :---- | :---- | :---- | :---- |
| Qtd de arquivos de ticket | > 10 | 1 | Redução de ruído e overhead mental. |
