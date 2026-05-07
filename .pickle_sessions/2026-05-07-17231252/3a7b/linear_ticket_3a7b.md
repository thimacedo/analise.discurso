---
id: 3a7b
title: Implementar Endpoint de API para Latência Individual do Worker
status: Todo
priority: High
order: 40
created: 2026-05-07
updated: 2026-05-07
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
A latência individual de cada worker precisa ser acessível via API para análise detalhada.

## Solution
Criar um endpoint na API que retorne as métricas de latência (média, p95, p99) para um worker específico, com base em seu ID.

## Implementation Details
- Definir o formato da resposta da API (incluindo worker ID).
- Implementar a lógica para buscar e retornar métricas de um worker específico.
- Considerar parâmetros para seleção de worker.
