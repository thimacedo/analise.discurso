# 📊 STATE.md - Sentinela Democrática

**Última Atualização:** 2026-05-16
**Versão Core:** PASA v47.10 (Diamond Edition)
**Status do Sistema:** Operação Estabilizada e Otimizada

## 1. Estado Atual do Ecossistema
O Sentinela Democrática opera agora com um backend serverless de alto desempenho no Vercel, integrado a um Nó Local robusto. A infraestrutura foi otimizada para manter o bundle size abaixo dos limites do Lambda (<300MB), permitindo escalabilidade sem comprometer a densidade analítica.

## 2. Componentes Principais (v47.10)

### Backend Serverless (Vercel)
- **API Engine:** FastAPI (Python 3.12) com `mangum` para Vercel.
- **Segurança:** Governança de sessões centralizada para gerenciamento de contas de raspagem.
- **Métricas:** Sistema de monitoramento de workers em tempo real (`workers_metrics`).
- **Otimização:** Bundle reduzido de 843MB para ~289MB através de exclusão estratégica de dependências locais e caches.

### Nó Local & Scraping
- **Governança de Sessões:** Interface web para injeção de cookies e controle de rotação automática.
- **Orquestrador:** Sincronização direta com Supabase para priorização de perfis e cooldowns.
- **Auto-healing:** Watchdog ativo com alertas de saúde do sistema.

### Inteligência Analítica
- **Modelagem:** Gemini 1.5 Flash + Groq (Llama 3) para auditoria cruzada.
- **Protocolo PASA:** Versionamento v47.10 com foco em métricas CCF e densidade de hostilidade.
- **Relatórios:** Motor de geração de PDFs (fpdf2) integrado à API para exportação de indícios.

## 3. Proteções Jurídicas e Acadêmicas
- **Nomenclatura:** Uso estrito de "Análise Analítica" e "Indícios de Risco" (PASA v47.x).
- **Isolamento:** Metodologia MSAL consolidada como padrão de processamento.
