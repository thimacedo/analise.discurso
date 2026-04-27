# ROADMAP.md - Sentinela Democratica

## Visao Geral
Plataforma Independente de Inteligencia Situacional. O sistema utiliza o Protocolo PASA v15.18 para monitoramento de crimes digitais.

## Status Atual: v15.18.2 (Selagem Arquitetural)
- [x] Documentacao de Processo: Criado docs/architecture/scraping-v15.md como guia definitivo.
- [x] Load Balancer: Distribuicao Round-Robin entre 3 APIs operacional.
- [x] Circuit Breaker: Protecao de creditos e isolamento de falhas validado.
- [x] Padrao de Evidencia: Sincronizado com metadados forenses (PASA).

## Proximos Passos
1. NLP Processor: Iniciar motor de classificacao em lote (Backlog 1000+ registros).
2. SQL Migracao: Adicao de classificacao_pasa (Acao Manual pendente).
3. Mobile View: Ajuste de colapso da sidebar Diamond.

## Protocolo de Estabilidade
- Arquitetura: Seguir estritamente o guia em docs/architecture/scraping-v15.md.
- Documentacao: Uso obrigatorio de compound-docs.
- Comunicacao: Texto puro sem emojis.

---
Atualizacao: 26/04/2026 | Versao: 15.18.2-stable
