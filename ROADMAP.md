# ROADMAP.md - Sentinela Democratica

## Visao Geral
Plataforma Independente de Inteligencia Situacional e Analise Forense. O sistema utiliza o Protocolo PASA v15.16 para monitoramento de crimes digitais e hostilidade politica via Llama 3.1.

## Status Atual: v15.16.2 (Estabilizacao de Dados)
- [x] Unificacao de Projeto: ID prj_hbfDAwwIfrz6nJgIkZWLNacCWpeq estabilizado.
- [x] Bypass de Automacao: Segredo de elite configurado para testes de producao.
- [x] Build Destravado: Correcao de requisitos e limpeza de caracteres invisiveis (BOM).
- [x] Higienizacao de Repositorio: Removidos arquivos temporarios e estabelecido .gitignore rigoroso.
- [x] Protocolo PASA: Mapeamento de dados via campo is_hate devido a limitacao de schema.

## Proximos Passos (Prioridade Maxima)
1. Migracao SQL: Adicionar coluna classificacao_pasa na tabela comentarios via Painel Supabase.
2. Alimentacao em Lote: Executar script de coleta para alvos com 0 registros.
3. Dossie PDF: Implementar exportacao de evidencias para fins juridicos.

## Protocolo de Estabilidade
- Estrutura: Arquivos HTML na raiz (Estaticos), pasta api/ para Python (Serverless).
- Dados: Cache-buster obrigatorio em todas as chamadas de API.
- Comunicacao: Texto puro sem emojis para garantir legibilidade em terminais legados.

---
Atualizacao: 26/04/2026 | Versao: 15.16.2-stable
