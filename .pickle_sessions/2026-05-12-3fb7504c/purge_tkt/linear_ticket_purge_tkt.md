---
id: purge_tkt
title: "Purga Final de Arquivos Legados"
status: "Done"
priority: "High"
order: 30
created: 2026-05-12
updated: 2026-05-12
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
Os arquivos antigos ainda estão lá, sujando o lugar.

## Solution
Deletar todos os arquivos identificados na fase de auditoria, garantindo que o CONSOLIDATED_BACKLOG.md e a sessão atual do Pickle Rick sejam preservados.

## Implementation Details
- Usar a lista da auditoria para deletar arquivos físicos.
- Limpar pastas vazias se necessário.

