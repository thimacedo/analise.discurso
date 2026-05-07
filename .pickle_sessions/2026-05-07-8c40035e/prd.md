# Raspagem Completa e Classificação de Comentários PRD

## HR Eng

| Raspagem Completa e Classificação de Comentários PRD |  | Solução para extração profunda, integração PASA e conformidade PSR-1 em scrapers críticos. |
| :---- | :---- | :---- |
| **Author**: Pickle Rick **Contributors**: N/A **Intended audience**: Engineering | **Status**: Draft **Created**: 2026-05-07 | **Context**: Refatoração e automação de extração de dados. |

## Introduction

Refatoração técnica necessária para garantir a robustez na extração de dados de redes sociais, aplicando o Protocolo PASA v16.4 e mantendo código limpo (PSR-1).

## Problem Statement

**Current Process:** Scrapers em `instagram_scraper.py`, `main_orchestrator.py` e `official_solenya_daemon.py` possuem lógica acoplada, falhas de resiliência e não seguem padrões de codificação unificados.
**Primary Users:** Sentinela Democrática.
**Pain Points:** Fragilidade na raspagem, lentidão no processamento, desvio do protocolo PASA.

## Objective & Scope

**Objective:** Estabilidade, conformidade e velocidade na extração.
**Ideal Outcome:** Um sistema resiliente que extrai, classifica via PASA e loga seguindo padrões PSR-1.

### In-scope or Goals
- [x] Refatoração de `instagram_scraper.py`.
- [x] Otimização de `main_orchestrator.py`.
- [x] Implementação PSR-1 em `official_solenya_daemon.py`.

### Not-in-scope or Non-Goals
- [ ] Adição de novas redes sociais.

## Product Requirements

### Critical User Journeys (CUJs)
1. **Extração Automática**: O daemon aciona o orquestrador, que gerencia os scrapers de forma resiliente.
2. **Classificação PASA**: Todos os comentários extraídos passam pelo auditor forense antes de serem persistidos.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | Integração PASA v16.4 | Como orquestrador, quero que cada comentário seja validado pelo PASA. |
| P0 | Conformidade PSR-1 | Como desenvolvedor, quero que o código respeite PSR-1. |
| P1 | Resiliência (Retry/Backoff) | Como scraper, quero que o sistema lide com bloqueios de rede de forma autônoma. |

## Assumptions

- A infraestrutura de conexão com as redes (Proxies/Instaloader) está disponível e configurada.

## Risks & Mitigations

- **Risk**: Bloqueios de scraping. -> **Mitigation**: Implementação de backoff exponencial e rotação de proxies (se aplicável).

## Tradeoff

- Optamos por refatoração em vez de reescrita total para manter a compatibilidade com o histórico de dados (Solenya Edition).

## Business Benefits/Impact/Metrics

**Success Metrics:**
- Taxa de sucesso de extração > 95%.
- Latência de classificação por comentário < 500ms.

## Stakeholders / Owners

| Name | Team/Org | Role | Note |
| :---- | :---- | :---- | :---- |
| Thiago | Engineering | Lead | Dev |
