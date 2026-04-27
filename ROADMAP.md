# ROADMAP.md - Sentinela Democratica

## Visao Geral
Plataforma Independente de Inteligencia Situacional. O sistema utiliza o Protocolo PASA v15.19 para monitoramento de crimes digitais.

## Status Atual: v15.19.0 (Intelligence Batch Edition)
- [x] Desacoplamento Analitico: Raspador e Classificador agora sao processos independentes.
- [x] NLP Batch Worker: Implementado motor BERTimbau (pysentimiento) para analise de hostilidade.
- [x] Schema Diamond: Adicionada tabela classificacoes e campos de processamento IA.
- [x] Fila de Inteligencia: Campo processado_ia gerencia o fluxo entre coleta e analise.

## Proximos Passos
1. Migracao de Dados: Processar o backlog de 1000+ registros via intelligence worker.
2. Dashboard Analitico: Implementar filtros por categoria PASA (Racismo, Sexismo, Ideologia).
3. Auditoria Judicial: Gerar relatorio detalhado unindo raw_metadata e veredito IA.

## Protocolo de Estabilidade
- Analise: Todo comentario deve ser limpo de links e mencoes antes de ser enviado a IA.
- Performance: O Intelligence Worker deve rodar em ambiente com min 2GB RAM.

---
Atualizacao: 26/04/2026 | Versao: 15.19.0-stable
