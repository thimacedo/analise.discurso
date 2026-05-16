---
id: gen_backlog
title: "Geração do Backlog Mestre Consolidado"
status: "Done"
priority: "High"
order: 20
created: 2026-05-12
updated: 2026-05-12
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
As tarefas pendentes estão fragmentadas.

## Solution
Com base no udit_report.json, filtrar apenas as tarefas que NÃO estão 'Done' e gerar um arquivo único CONSOLIDATED_BACKLOG.md no diretório raiz.

## Implementation Details
- Ler o relatório de auditoria.
- Formatar as tarefas pendentes em uma lista Markdown limpa.
- Salvar no root.

