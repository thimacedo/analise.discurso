---
id: 4a2b
title: Implementar Endpoint de API para Latência Agregada
status: Todo
priority: High
order: 10
created: 2026-05-07
updated: 2026-05-07
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
A latência agregada dos workers precisa ser exposta via API para ser consumida pelo frontend do dashboard.

## Solution
Criar um endpoint na API que retorne as métricas de latência agregadas (média, p95, p99) de todos os workers.

## Implementation Details
- Definir o formato da resposta da API.
- Implementar a lógica no backend para coletar e agregar as métricas.
- Garantir que o endpoint seja performático.
