---
id: parent-ticket-placeholder # Placeholder ID, will be replaced by a generated hash
title: "[Epic] Melhorar Raspagem, Classificação e Sistema de Recompensa"
status: Backlog
priority: High
order: 0
created: 2026-05-07
updated: 2026-05-07
links:
  - url: ../prd.md
    title: PRD
---

# Description

## Problem to solve
A necessidade de garantir a operacionalidade completa da rotina de extração de dados, a integração eficaz da classificação de comentários (PSR-1) e a plena ativação do sistema de recompensas para os workers. O objetivo é ter um sistema robusto, eficiente e aderente aos padrões do projeto.

## Solution
Implementar e verificar a funcionalidade completa do `instagram_scraper.py`, integrar a classificação de comentários PSR-1 e garantir que o `official_solenya_daemon.py` esteja ativo e operante, gerenciando recompensas PSR-1 para workers.

## Implementation Details
- Análise e validação dos arquivos: `instagram_scraper.py`, `main_orchestrator.py`, `official_solenya_daemon.py`, `README.md`.
- Implementar/Verificar raspagem completa.
- Integrar classificação de comentários PSR-1.
- Ativar e operar sistema de recompensas PSR-1 nos workers.
- Garantir conformidade com `README.md`.
