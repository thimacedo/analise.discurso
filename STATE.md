# Estado Atual do Sistema - SENTINELA | Diamond Edition

## 💎 Versão: 19.2.4 (PASA Persistence Ready)
- **Data da última atualização:** 29/04/2026
- **Status:** Pipeline de persistência forense implementado. Aguardando validação de schema e execução de teste.

## ✅ O que está funcionando
- **API Proxy (FastAPI):** Endpoints (`/trends`, `/pasa/breakdown`) consumindo dados de inteligência persistidos. Eliminação de processamento em tempo real.
- **Pipeline (Orquestrador):** Integração com `tools/persistence.py`. Resultados PASA (`is_hate`, `categoria_ia`) sendo gravados em tempo real no Supabase.
- **Checkout:** Preço do plano Pro atualizado para R$ 279,90.
- **Frontend (Diamond UI):** Dashboard dinâmico e mapa geopolítico.

## 🚫 Abordagens Descartadas
- **[DESCARTADO] Classificação PASA em tempo real no Dashboard:** Inviável para escala. Substituído por persistência em banco via Worker e leitura via API.
- **[DESCARTADO] Conexão Direta Supabase no Frontend:** Inseguro. Substituído por API Proxy.

## 🐛 Bugs Atuais / Bloqueios
- **Schema Pendente:** As colunas `is_hate_speech` e `pasa_category` ainda precisam ser criadas no Supabase via painel SQL.
- **Validação Fim-a-Fim:** Necessário rodar `python orquestrador.py` para confirmar que o `upsert` do `persistence.py` não retorna erros de constraint do banco.
