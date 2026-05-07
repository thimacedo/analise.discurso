---
id: a9e2
title: Desenvolver Componente Frontend para Exibição de Latência Individual (Gráficos)
status: Todo
priority: High
order: 60
created: 2026-05-07
updated: 2026-05-07
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
A visualização detalhada da latência de workers individuais precisa ser apresentada de forma gráfica e informativa.

## Solution
Criar um componente frontend que consuma o endpoint de API de latência individual e exiba as métricas em gráficos de linha interativos.

## Implementation Details
- Integrar com uma biblioteca de gráficos (ex: Chart.js, Recharts).
- Consumir o endpoint de API de latência individual.
- Configurar os gráficos para exibir latência média, p95, p99.
- Garantir a interatividade dos gráficos (ex: tooltips).
