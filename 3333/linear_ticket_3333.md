---
id: 3333
title: "Migrate Alerter Logic"
status: Todo
priority: High
order: 30
created: 2026-05-02
updated: 2026-05-02
links:
  - url: ../linear_ticket_parent.md
    title: Parent Ticket
---

# Description

## Problem to solve
Substituir o CallMeBot pela lógica do Firebase para os alertas de pericia.

## Solution
Atualizar o serviço de alerta para publicar eventos no FCM.

## Implementation Details
- Modificar o `whatsapp_alerter.py` (ou criar novo alerta) para usar FCM.
- Validar envio de notificações de teste.
