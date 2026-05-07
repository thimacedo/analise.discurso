---
id: f0d1
title: Criar Serviço Backend para Obtenção de Latência Individual
status: Todo
priority: High
order: 50
created: 2026-05-07
updated: 2026-05-07
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
É necessário um serviço backend que possa acessar e fornecer métricas de latência para workers individuais.

## Solution
Desenvolver um serviço backend que consulta as métricas de latência de um worker específico e as disponibiliza para o endpoint de API correspondente.

## Implementation Details
- Implementar a consulta de métricas por worker ID.
- Preparar os dados para o formato esperado pelo endpoint de API.
- Garantir a eficiência na consulta para workers individuais.
