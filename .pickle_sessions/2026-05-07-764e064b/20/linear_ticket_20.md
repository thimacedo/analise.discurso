---
id: 20
title: "Implementar Cooldown Inteligente no Daemon"
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

## Problem
Agressividade excessiva causa bloqueio de IP.

## Solution
Implementar lógica de `exponential backoff` e cooldown dinâmico no `official_solenya_daemon.py`.
