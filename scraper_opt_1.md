---
id: scraper_opt_1
title: "Otimizar e Expandir Scrapers de Dados"
status: Todo
priority: High
order: 10
created: 2026-05-07
updated: 2026-05-07
links:
  - url: ../linear_ticket_epic_solenya_pipeline_rewards.md
    title: Parent Ticket
---

# Description

## Problem to solve
A coleta de dados pode ser incompleta e menos eficiente do que o potencial máximo.

## Solution
Melhorar os scrapers existentes (Instagram, Meta) e considerar novas fontes.

## Implementation Details
- Analisar `instagram_scraper.py` e `sentinela_scraper/spiders/instagram.py`.
- Implementar robustez contra mudanças de DOM no Instagram.
- Avaliar a viabilidade de adicionar scrapers para outras plataformas (TikTok, YouTube).
- Garantir que todos os metadados relevantes sejam coletados.
