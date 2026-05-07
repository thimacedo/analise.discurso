---
id: 7b3c
title: Implementar Exibição de Taxas de Erro no Dashboard
status: Todo
priority: Medium
order: 70
created: 2026-05-07
updated: 2026-05-07
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
Informações sobre taxas de erro dos workers são importantes para correlacionar com a latência e diagnosticar problemas.

## Solution
Integrar a exibição das taxas de erro (agregadas e/ou individuais) no dashboard, permitindo a correlação visual com as métricas de latência.

## Implementation Details
- Identificar como as taxas de erro são coletadas/expostas.
- Criar endpoints de API ou modificar existentes para incluir dados de erro.
- Desenvolver componentes frontend para exibir as taxas de erro de forma clara.
- Considerar a visualização de taxas de erro em tabelas e/ou gráficos.
