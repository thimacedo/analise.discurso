---
id: parent-dashboard-latency
title: "[Epic] Dashboard de Métricas de Latência dos Workers"
status: Backlog
priority: High
order: 0
created: 2026-05-07
updated: 2026-05-07
links: []
---

# Description

## Problem to solve
O sistema atual carece de visibilidade sobre a latência dos workers, dificultando a identificação de gargalos de performance e a otimização do sistema.

## Solution
Implementar um dashboard dedicado que exiba métricas de latência (média, p95, p99) e taxas de erro dos workers, permitindo monitoramento em tempo real e análise histórica.

## Implementation Details
- Criação de endpoints de API para expor as métricas.
- Desenvolvimento de serviços backend para coletar e processar dados de latência.
- Implementação de componentes frontend para visualização de dados, incluindo tabelas e gráficos.
- Integração com a arquitetura BaseWorker v2.0.
- Funcionalidades de filtro de tempo e exibição de taxas de erro.
