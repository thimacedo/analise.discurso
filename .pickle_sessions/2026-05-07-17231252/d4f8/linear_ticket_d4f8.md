---
id: d4f8
title: Adicionar Funcionalidade de Filtro de Intervalo de Tempo no Frontend
status: Todo
priority: Medium
order: 80
created: 2026-05-07
updated: 2026-05-07
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
Usuários precisam de flexibilidade para analisar a performance em diferentes períodos de tempo.

## Solution
Implementar um seletor de intervalo de tempo no frontend do dashboard, permitindo aos usuários filtrar os dados exibidos (ex: últimas 24 horas, últimos 7 dias, intervalo customizado).

## Implementation Details
- Adicionar componentes de seleção de data/hora no UI.
- Atualizar as chamadas de API para incluir parâmetros de intervalo de tempo.
- Garantir que os gráficos e tabelas reajam corretamente à mudança de filtro.
