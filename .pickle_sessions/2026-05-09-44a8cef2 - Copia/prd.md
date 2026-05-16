# Sentinela Democrática v20.6 - Estabilização, Resiliência e Monetização PRD

## HR Eng

| Feature Name | PRD v20.6 | Estabilização crítica do Sentinela Democrática para mitigar crashes de memória, falhas de renderização e perda de receita. |
| :---- | :---- | :---- |
| **Author**: Pickle Rick **Contributors**: Morty (o assistente inútil) | **Status**: Solenya (Pronto para Execução) **Created**: 2026-05-09 | **Context**: Milestone de Resiliência |

## Introduction

O projeto "Sentinela Democrática" atingiu um ponto de saturação técnica. O frontend é frágil, o backend vaza memória como um balde furado e a monetização é meramente decorativa porque os IDs estão errados. Esta milestone foca em blindar o sistema contra a incompetência sistêmica e garantir que a escala de dados não derrube a infraestrutura.

## Problem Statement

**Current Process:** Carregamento massivo de dados via API, injeção direta de DOM sem verificações de nulidade e uso de IDs de teste em produção.
**Primary Users:** Analistas de dados, equipes de monitoramento político e o financeiro (que quer ver dinheiro entrando).
**Pain Points:**
- **Frontend Colapse:** Erros de `undefined.length` travam o dashboard se a API falhar.
- **Cache Hell:** Navegadores servem scripts velhos, ignorando correções críticas.
- **Memory Leak:** OOM (Out of Memory) matando processos Node.js com 7.4GB+ de RAM.
- **Revenue Gap:** AdSense e Stripe falhando por IDs inválidos e slots mal configurados.
**Importance:** Se não estabilizarmos agora, o sistema é inútil. Um sentinela que dorme no posto (ou morre por falta de RAM) não serve para nada.

## Objective & Scope

**Objective:** Criar um frontend tolerante a falhas, otimizar o consumo de memória via paginação estrita e validar o fluxo de caixa (Stripe/AdSense).
**Ideal Outcome:** Zero White Screens, carregamento inicial < 2s, 100% de sucesso nas chamadas de anúncios e pagamentos.

### In-scope ou Goals
- Implementação de Fallbacks de UI (Skeleton screens ou Empty States) para falhas de API.
- Cache Busting via query strings ou Headers HTTP.
- Limite de 20 itens no fetch inicial (`dataService`).
- Substituição de IDs fictícios por variáveis de ambiente/IDs de produção.
- Robustez nos seletores de scraping (Regex Fallbacks).
- **Purga de Workers (Ruthless Refactor)**: Consolidação de serviços redundantes e remoção de referências a workers obsoletos.

### Not-in-scope ou Non-Goals
- Novas features de visualização de dados (foco é estabilidade).
- Refatoração completa para React/Vue (vamos consertar o Vanilla JS primeiro).

## Product Requirements

### Critical User Journeys (CUJs)
1. **Dashboard Sobrevivente**: O usuário abre o dashboard com a API offline. Em vez de tela branca, ele vê uma mensagem de "Sistema em Manutenção" ou dados cacheados, mas a UI não quebra.
2. **Infinite Scroll Otimizado**: O usuário rola o feed; o sistema carrega os próximos 20 itens de forma transparente sem estourar a Heap do navegador.
3. **Checkout Real**: O usuário clica em assinar e é redirecionado para o Stripe real, não para uma página de erro de "Price ID Not Found".

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | Frontend Null-Safety | Garantir que `summary`, `targets` e `alerts` sejam sempre arrays/objetos válidos. |
| P0 | Pagination Limit (Max 20) | O sistema deve recusar carregar mais de 20 itens no `init`. |
| P0 | Monetization IDs Fix | Trocar `SIDEBAR_DIAMOND` e `price_1Starter` por IDs funcionais. |
| P1 | Cache Busting Strategy | Versionar arquivos `app.js` e `ui.js` no `index.html`. |
| P1 | Regex Scraper Fallback | Se `span[dir="auto"]` falhar, usar regex para extrair texto bruto. |
| P2 | Zombie Process Killer | Script para limpar portas 8000/8080 antes do boot de dev. |

## Assumptions

- O Supabase suporta filtros de `limit` e `offset` (Spoilers: suporta).
- As variáveis de ambiente do AdSense estão disponíveis no painel de controle.

## Risks & Mitigations

- **Risk**: Cache de CDN ignorar o cache-busting -> **Mitigation**: Cabeçalhos `Cache-Control` agressivos no Vercel.
- **Risk**: Scraper ser bloqueado por mudanças no Instagram -> **Mitigation**: Uso de headless proxies e rotação de headers.

## Tradeoff

- Escolhemos limitar o carregamento inicial em vez de otimizar o backend agora. Isso melhora o TTI (Time to Interactive) imediatamente, mesmo que exija mais requisições durante o scroll.

## Business Benefits/Impact/Metrics

**Success Metrics:**

| Metric | Current State | Future State | Impact |
| :---- | :---- | :---- | :---- |
| Uptime Frontend | 70% (quebra com API) | 99.9% (resiliente) | Estabilidade |
| Memory Usage | 7.4GB (Crashes) | < 1GB por processo | Redução de custo/estabilidade |
| CTR AdSense | 0% (Erro 400) | > 2% | Receita |

## Stakeholders / Owners

| Name | Team/Org | Role | Note |
| :---- | :---- | :---- | :---- |
| Pickle Rick | God Tier Engineering | Grand Overseer | Dono da verdade |
| Morty | Jerry Tier | Worker | Para carregar as coisas pesadas |
