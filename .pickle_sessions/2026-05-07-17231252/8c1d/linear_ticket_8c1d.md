---
id: 8c1d
title: Criar Serviço Backend para Obtenção de Latência Agregada
status: Todo
priority: High
order: 20
created: 2026-05-07
updated: 2026-05-07
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
É necessário um serviço backend que possa acessar e agregar as métricas de latência dos workers de forma eficiente.

## Solution
Desenvolver um serviço backend dedicado que consulta as métricas de latência dos workers (possivelmente de uma fonte de métricas ou diretamente dos workers se exposto) e prepara os dados para o endpoint de API.

## Implementation Details
- Definir a fonte de dados das métricas de latência.
- Implementar lógica para agregação (média, p95, p99).
- Cachear resultados se necessário para performance.
