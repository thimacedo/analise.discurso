---
date: "2026-04-26"
problem_type: "resource-exhaustion"
severity: "high"
symptoms:
  - "Gasto desnecessario de creditos em APIs instaveis"
  - "Tempo de execucao alto (50min+ para 242 alvos)"
  - "Falhas em cascata ao atingir Rate Limits do Instagram"
root_cause: "monolithic-sequential-scraping"
tags:
  - reliability
  - performance
  - load-balancer
  - rapidapi
---

# Solucao: Orquestracao Multi-API com Circuit Breaker

## Diagnostico
O sistema dependia de uma unica API e processava alvos de forma sequencial. Quando o Instagram bloqueava o proxy da API ou a cota acabava, o script continuava tentando os alvos restantes, desperdiçando tempo e creditos da RapidAPI.

## Acoes Tomadas
1. Load Balancer Round-Robin: Criada a classe LoadBalancer para distribuir alvos entre 3 provedores distintos simultaneamente.
2. Circuit Breaker: Implementada logica que detecta 3 falhas consecutivas em uma API e a isola por 15 minutos (cooldown).
3. Processamento em Lotes Assincronos: Migracao para asyncio.gather processando 6 alvos por vez (2 por API).

## Licoes Aprendidas
- Sistemas de raspagem devem ser sempre multi-fonte para evitar single-point-of-failure.
- O custo de uma falha deve ser mitigado via software (Circuit Breaker) para proteger o orçamento do projeto.
