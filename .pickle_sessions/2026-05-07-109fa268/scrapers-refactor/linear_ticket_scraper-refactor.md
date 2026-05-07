---
id: scraper-refactor
title: Refatoração dos Scrapers Instagram e Orquestrador
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
Scrapers em `instagram_scraper.py` e `main_orchestrator.py` possuem lógica acoplada e falta de resiliência.

## Solution
Implementar interfaces `BaseWorker` e garantir resiliência.

## Implementation Details
- Refatorar `instagram_scraper.py` e `main_orchestrator.py`.
