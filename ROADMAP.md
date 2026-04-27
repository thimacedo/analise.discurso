# ROADMAP.md - Sentinela Democratica

## Visao Geral
Plataforma Independente de Inteligencia Situacional. O sistema utiliza o Protocolo PASA v15.18 para monitoramento de crimes digitais.

## Status Atual: v15.18.1 (Resiliencia de Custo e Carga)
- [x] Load Balancer: Distribuicao Round-Robin entre 3 APIs RapidAPI operacional.
- [x] Circuit Breaker: Mecanismo de isolamento de APIs falhas validado em producao.
- [x] Protecao de Creditos: Sistema evita tentativas inuteis em endpoints bloqueados ou sem cota.
- [x] Saneamento de Ambiente: Codificacao UTF-8 e comunicacao em texto puro consolidadas.

## Proximos Passos (Prioridade Alta)
1. NLP Processor: Desenvolver motor de classificacao PASA v15.16 utilizando Llama 3.1.
2. Migracao SQL: Adicionar coluna classificacao_pasa na tabela comentarios (Acao Manual pendente).
3. Backlog Audit: Processar os registros ja existentes (Lula, Tarcisio, etc) com a nova Skill Forensic.

## Protocolo de Estabilidade
- Arquitetura: Padrao Diamond com separacao estrita entre Coleta (Python) e Exibicao (HTML Estatico).
- Documentacao: Todo erro arquitetural resolvido deve ser registrado em docs/solutions/.
- Seguranca: Uso de bypass oficial para auditorias automatizadas no Vercel.

---
Atualizacao: 26/04/2026 | Versao: 15.18.1-stable
