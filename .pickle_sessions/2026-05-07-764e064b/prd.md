# PRD: Ciclo de Stress-Test e Auto-Refatoração Noturna

## HR Eng

| Stress-Test & Auto-Refatoração |  | Automatização de testes de carga e resiliência forense com auto-cura. |
| :---- | :---- | :---- |
| **Author**: Pickle Rick | **Status**: Draft **Created**: 2026-05-07 | **Context**: Estabilidade de alta performance para extração de dados forenses (PASA v16.4). |

## Introduction

Este projeto visa implementar um ciclo de testes automatizados de stress que dispara mecanismos de auto-refatoração ao detectar falhas operacionais (403/Bloqueios) durante a extração de dados do Instagram pelo Sentinela Democrática.

## Problem Statement

**Current Process:** Raspagens manuais ou isoladas sem resiliência.
**Pain Points:** Bloqueios frequentes do Instagram (403), falta de feedback em tempo real para o sistema.
**Importance:** Vital para manter o fluxo de dados em larga escala para auditoria forense.

## Objective & Scope

**Objective:** Alcançar Rank Ultra-S (200 pontos) garantindo 5 perfis processados sem falhas de acesso.
**Ideal Outcome:** Um sistema que se auto-corrige e escala durante a madrugada.

### In-scope
- Desenvolvimento de `tests/stress_test.py`.
- Integração de sistema de Cooldown Inteligente.
- Auto-refatoração de módulos `stealth` e `behavior`.

### Not-in-scope
- Refatoração da UI do dashboard.

## Product Requirements

### Critical User Journeys (CUJs)
1. **Stress Cycle**: O sistema seleciona 10 perfis -> executa raspagem -> detecta 403 -> dispara refatoração -> reinicia ciclo.
2. **Auto-Cura**: Sistema aplica cooldown dinâmico se a taxa de falha exceder limite.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | Teste de Carga 10 Perfis | Como sistema, quero rodar batch de 10 perfis. |
| P0 | Auto-Refatoração | Como scraper, quero corrigir minha estratégia ao falhar. |
| P1 | Cooldown Inteligente | Como daemon, quero pausar e retomar com inteligência. |

## Risks & Mitigations

- **Risk**: IP Block permanente -> **Mitigation**: Rotação agressiva e Cooldown exponencial.

## Success Metrics

| Metric | Target | Impact |
| :---- | :---- | :---- |
| Pontos (PSR-R) | 200 (Ultra-S) | Estabilidade Total |
| Perfis OK | 5 Seguidos | Resiliência |
