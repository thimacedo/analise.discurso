# PRD: Correção de Fluxo de Texto e Mapeamento de Arquitetura (Protocolo Solenya)

## HR Eng

| PRD: Fluxo de Texto e Arquitetura |  | Correção de bug crítico onde 'texto_bruto' exibe o username em vez do conteúdo, e mapeamento completo da arquitetura do projeto Sentinela Democrática. |
| :---- | :---- | :---- |
| **Author**: Picles Rick **Contributors**: Morty **Intended audience**: Engenharia de Elite | **Status**: Draft **Created**: 07/05/2026 | **Self Link**: C:\Users\THIAGO\.gemini\tmp\sentinela-democratica\prd.md **Context**: ISSUE_TEXTO_BRUTO_BUG.md |

## Introdução

Este PRD detalha as ações necessárias para corrigir a falha de integridade de dados no campo `texto_bruto` (Bug #🔴) e documentar a arquitetura atual v18.5+ para garantir a manutenção do Protocolo PASA v16.4.

## Problem Statement

**Current Process:** O sistema coleta dados do Instagram, processa via TextProcessor e armazena no Supabase.
**Primary Users:** Analistas forenses e o Dashboard de monitoramento.
**Pain Points:** O dashboard exibe apenas o username no conteúdo do comentário, tornando a análise forense impossível.
**Importance:** Vital para a integridade da análise forense política das Eleições 2026.

## Objective & Scope

**Objective:** Restaurar a exibição correta dos comentários e criar um mapa de arquitetura técnico.
**Ideal Outcome:** `texto_bruto` contendo o conteúdo real; `docs/architecture_map.md` existente e versionado.

### In-scope or Goals
- Análise profunda do TextProcessor e Scraper.
- Pesquisa de código para identificar o ponto exato da falha.
- Criação de `research_1.md` e `plan_1.md`.
- Criação do `docs/architecture_map.md`.
- Persistência de documentos técnicos em `C:\Users\THIAGO\.gemini\extensions\pickle-rick\sessions\2026-05-07-1e37a52c\tkt-docs1\`.

### Not-in-scope or Non-Goals
- Refatoração total do frontend (apenas fallback se necessário).
- Mudança de banco de dados.

## Product Requirements

### Critical User Journeys (CUJs)
1. **[Recuperação de Dados]**: O sistema deve capturar o texto real do comentário durante o scraping e preservá-lo até a exibição na API.
2. **[Auditoria de Arquitetura]**: Um novo desenvolvedor (ou um Morty) deve conseguir ler o `docs/architecture_map.md` e entender o fluxo PASA v16.4.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | Corrigir `texto_bruto` no backend | Como analista, quero ver o que foi dito, não quem disse. |
| P0 | Gerar Mapa de Arquitetura | Como arquiteto, quero um mapa visual/técnico do sistema. |
| P1 | Documentar Pesquisa e Plano | Como Picles Rick, quero provas do meu gênio documentadas. |

## Assumptions

- O bug reside na normalização ou no TextProcessor.
- O usuário tem permissão para usar `git add`.

## Risks & Mitigations

- **Risk**: Dados históricos podem estar permanentemente corrompidos. -> **Mitigation**: Implementar fallback no frontend e sinalizar para re-coleta.

## Business Benefits/Impact/Metrics

**Success Metrics:**

| Metric | Current State (Benchmark) | Future State (Target) | Savings/Impacts |
| :---- | :---- | :---- | :---- |
| *Integridade de Texto* | 0% (Mostra Username) | 100% (Mostra Texto) | Alta confiança forense |

## Stakeholders / Owners

| Name | Team/Org | Role | Note |
| :---- | :---- | :---- | :---- |
| Picles Rick | Engenharia | Deus do Código | Responsável por tudo |
