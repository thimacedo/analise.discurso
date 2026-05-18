---
id: tkt_fix_text_1
title: "Investigar e Corrigir Integridade do Campo texto_bruto"
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
O dashboard exibe o username no lugar do conteúdo do comentário devido à corrupção no campo `texto_bruto`.

## Solution
Analisar `sentinela_scraper/instagram.py`, `processing/text_processor.py` e `core/normalizer.py`. Corrigir a extração e o processamento de texto.

## Implementation Details
- Criar `research_1.md` com o diagnóstico.
- Criar `plan_1.md` com a correção.
- Implementar correção no backend.
- Persistir docs em `tkt-docs1`.
