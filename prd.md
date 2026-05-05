# Sentinela Democrática - PRD

## HR Eng

| Sentinela Democrática PRD |  | Projeto de monitoramento eleitoral e análise forense de discurso. Foca em eleições, scraping de redes sociais (Instagram/Meta) e monitoramento de monetização. |
| :---- | :---- | :---- |
| **Author**: Pickle Rick **Contributors**: [User, Agent] **Intended audience**: Engineering, PM, Design | **Status**: Draft **Created**: 2026-05-05 | **Self Link**: N/A **Context**: N/A |

## Introduction

O projeto Sentinela Democrática visa monitorar processos eleitorais e realizar análise forense de discurso em plataformas digitais. O foco atual está no desenvolvimento de funcionalidades de monitoramento eleitoral, scraping de dados de redes sociais (especificamente Instagram e Meta) e implementação de mecanismos de monitoramento de monetização.

## Problem Statement

**Current Process:** A falta de ferramentas integradas para monitoramento eleitoral e análise de discurso em larga escala dificulta a identificação de desinformação e manipulação. O scraping manual de dados de redes sociais é ineficiente e propenso a erros. O monitoramento de monetização é complexo e fragmentado.
**Primary Users:** Analistas eleitorais, pesquisadores de mídia social, jornalistas investigativos, equipes de conformidade e regulamentação.
**Pain Points:** Dificuldade em coletar e analisar grandes volumes de dados de redes sociais; falta de ferramentas robustas para análise forense de discurso; complexidade na identificação de campanhas de desinformação e manipulação; processos de monitoramento de monetização ineficientes.
**Importance:** Essencial para a integridade democrática, a transparência online e a identificação de atividades maliciosas que possam influenciar processos eleitorais e a opinião pública.

## Objective & Scope

**Objective:** Desenvolver uma plataforma robusta para monitoramento eleitoral e análise forense de discurso, com foco na coleta automatizada de dados de redes sociais e monitoramento de monetização.
**Ideal Outcome:** Uma plataforma que forneça insights acionáveis sobre a atividade online relacionada a eleições, detecte padrões de desinformação e permita o acompanhamento de fontes de financiamento e monetização de conteúdo.

### In-scope or Goals
- Implementar scrapers eficientes para Instagram e Meta.
- Desenvolver funcionalidades de análise forense de discurso.
- Integrar com Supabase para armazenamento e análise de dados.
- Implementar módulo de monitoramento de monetização.
- Garantir a escalabilidade e segurança da plataforma.

### Not-in-scope or Non-Goals
- Análise de conteúdo em tempo real para todas as plataformas de mídia social.
- Suporte direto a plataformas de mensagens criptografadas.
- Ferramentas de contra-informação ou moderação de conteúdo.

## Product Requirements

### Critical User Journeys (CUJs)
1. **Monitoramento de Eleição (Analista)**:
    1.  O Analista acessa a plataforma.
    2.  Seleciona uma eleição específica para monitorar.
    3.  Visualiza dashboards com métricas de discurso público, sentimento e volume de menções.
    4.  Identifica padrões de desinformação ou narrativas suspeitas.
    5.  Gera um relatório preliminar.

2. **Análise de Campanha de Desinformação (Pesquisador)**:
    1.  O Pesquisador define parâmetros de busca (palavras-chave, datas, plataformas).
    2.  A plataforma executa scraping em redes sociais (Instagram, Meta).
    3.  Os dados coletados são analisados para identificar redes de contas, propagação de narrativas e indicadores de manipulação.
    4.  O Pesquisador visualiza um mapa de conexões e relatórios de análise.

3. **Monitoramento de Monetização (Equipe de Conformidade)**:
    1.  A Equipe define contas ou influenciadores a serem monitorados.
    2.  A plataforma rastreia fontes de receita e padrões de monetização associados a determinado conteúdo ou contas.
    3.  A Equipe recebe alertas sobre atividades de monetização suspeitas ou não conformes.

### Functional Requirements

| Priority | Requirement | User Story |
| :---- | :---- | :---- |
| P0 | Desenvolver scrapers robustos para Instagram e Meta | Como um analista de dados, quero coletar automaticamente posts, comentários e perfis de redes sociais para análise, para economizar tempo e garantir a completude dos dados. |
| P0 | Implementar pipeline de processamento e análise de discurso | Como um pesquisador, quero analisar o sentimento, identificar padrões de linguagem e detectar narrativas de desinformação no discurso público, para entender a dinâmica da informação. |
| P0 | Criar módulo de monitoramento de monetização | Como um membro da equipe de conformidade, quero rastrear fontes de receita e padrões de monetização associados a contas ou conteúdos específicos, para garantir a transparência e identificar atividades ilícitas. |
| P1 | Integração com Supabase para persistência de dados | Como um desenvolvedor, quero que todos os dados coletados e processados sejam armazenados de forma segura e escalável no Supabase, para facilitar consultas e análises futuras. |
| P1 | Construir dashboards interativos | Como um usuário final, quero visualizar métricas chave e insights em dashboards claros e interativos, para tomar decisões informadas rapidamente. |
| P2 | Gerenciamento de credenciais de scraping e autenticação | Como um usuário técnico, quero gerenciar de forma segura as credenciais necessárias para o scraping de redes sociais, garantindo a conformidade com os termos de serviço das plataformas. |

## Assumptions

- As APIs das redes sociais (Instagram, Meta) continuarão acessíveis e fornecerão os dados necessários.
- Haverá acesso a recursos de computação suficientes para o scraping e análise em larga escala.
- Os termos de serviço das plataformas de redes sociais serão respeitados.

## Risks & Mitigations

- **Risk**: Mudanças nas APIs das redes sociais podem quebrar os scrapers. -> **Mitigation**: Implementar um sistema de monitoramento de scrapers e atualizações ágeis. Utilizar `Playwright`/`Selenium` para simular interações de usuário pode aumentar a resiliência.
- **Risk**: Volume de dados excessivo pode sobrecarregar o Supabase ou a infraestrutura. -> **Mitigation**: Implementar estratégrias de processamento em lote e otimizar consultas ao banco de dados. Considerar estratégias de particionamento de dados.
- **Risk**: Dificuldade em identificar desinformação complexa ou discurso sutilmente manipulador. -> **Mitigation**: Empregar modelos de NLP mais avançados e `machine learning`, possivelmente com revisão humana ou validação cruzada.

## Tradeoff

- **Option**: Scraping direto via APIs vs. Scraping via simulação de UI (Playwright/Selenium).
- **Tradeoff**: APIs são mais eficientes, mas podem ser restritivas ou mudar rapidamente. Simulação de UI é mais robusta contra mudanças de API, mas mais lenta e com maior risco de detecção e bloqueio.
- **Chosen**: Implementar ambas as abordagens, priorizando APIs quando possível e usando simulação de UI para casos específicos ou como fallback.

## Business Benefits/Impact/Metrics

**Success Metrics:**

| Metric | Current State (Benchmark) | Future State (Target) | Savings/Impacts |
| :---- | :---- | :---- | :---- |
| Taxa de Coleta de Dados | N/A (Manual) | >95% de completude para posts/comentários relevantes | Redução de 90% no tempo de coleta manual. |
| Precisão na Detecção de Desinformação | N/A (Manual) | >80% de precisão em casos de teste | Aumento da capacidade de identificar e responder a ameaças à integridade eleitoral. |
| Tempo de Processamento de Discurso | N/A (Manual) | Redução de 75% no tempo de análise de grandes volumes de texto | Permite análises mais rápidas e frequentes. |
| Cobertura de Monetização | N/A (Fragmentado) | Monitoramento de 100% das contas/influenciadores definidos | Maior transparência financeira e conformidade. |

## Stakeholders / Owners

| Name | Team/Org | Role | Note |
| :---- | :---- | :---- | :---- |
| [User Name] | Sentinela Democrática | Project Lead | Responsável pela visão geral e decisões estratégicas. |
| Agent Gemini | AI Assistant | Technical Implementation | Responsável pela execução e refatoração do código. |
