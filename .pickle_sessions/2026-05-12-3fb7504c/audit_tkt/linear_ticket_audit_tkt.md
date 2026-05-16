---
id: audit_tkt
title: "Auditoria e Extração de Tickets Legados"
status: "Done"
priority: "High"
order: 10
created: 2026-05-12
updated: 2026-05-12
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
Existem dezenas de arquivos de ticket espalhados. Precisamos de um inventário completo do que está neles.

## Solution
Criar um script temporário ou usar comandos de shell para ler o conteúdo de todos os tickets identificados e salvar um resumo (JSON ou CSV) com: Caminho, Título, Status e Descrição Curta.

## Implementation Details
- Iterar sobre a lista de arquivos .md encontrados.
- Parsear frontmatter e corpo.
- Gerar udit_report.json.

