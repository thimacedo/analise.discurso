# ROADMAP.md - Sentinela Democratica

## Visao Geral
Plataforma Independente de Inteligencia Situacional. O sistema utiliza o Protocolo PASA v15.19 para monitoramento de crimes digitais.

## Status Atual: v15.19.1 (Automation Edition)
- [x] Intelligence Worker: Criado workflow .github/workflows/intelligence_worker.yml.
- [x] Automacao Agendada: Sistema pronto para rodar a cada 30 min no GitHub Actions.
- [x] Desacoplamento Analitico: Inteligencia removida do coletor para ganho de performance.

## Proximos Passos
1. Configurar Secrets: Adicionar SUPABASE_URL e SUPABASE_KEY no GitHub.
2. Migracao SQL: Adicionar classificacao_pasa no banco para salvar vereditos detalhados.
3. Dashboard Analitico: Exibir a categoria PASA nos cards de alerta.

## Protocolo de Estabilidade
- Inteligencia: Sempre rodar o worker de IA em ambiente isolado (min 4GB RAM).
- Documentacao: Manter compound-docs atualizado para toda mudanca em workflows.

---
Atualizacao: 26/04/2026 | Versao: 15.19.1-stable
