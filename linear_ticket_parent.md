---
id: parent-firebase-push
title: "[Epic] Firebase Push Notifications"
status: Backlog
priority: High
order: 10
created: 2026-05-02
updated: 2026-05-02
links:
  - url: ROADMAP.md
    title: Roadmap v20.1
---

# Description

## Problem to solve
O sistema atual usa o CallMeBot para alertas de WhatsApp, que é instável e dependente de serviços externos. Precisamos de uma solução nativa de Notificações Push via Firebase Cloud Messaging no Dashboard do Sentinela.

## Solution
Implementar o Firebase Cloud Messaging para alertas em tempo real.

## Implementation Details
- Integrar SDK do Firebase ao projeto.
- Configurar Dashboard para receber e exibir notificações.
- Migrar lógica de alertas.
