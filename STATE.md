# Estado Atual do Sistema - SENTINELA | Diamond Edition

## 💎 Versão: 19.0.0
- **Data da última atualização:** 29/04/2026
- **Status:** Fundação Diamond Edition implementada e em teste (Vercel Preview).

## ✅ O que está funcionando
- **API Proxy (FastAPI):** Centraliza requisições, remove segredos do frontend. Endpoints `/trends`, `/geo/uf`, `/pasa/breakdown`, `/targets` ativos.
- **Banco de Dados (Supabase):** Tabelas `metricas_diarias`, `redes_coordenadas`, `alertas_ativos` e views de score prontas no script SQL.
- **Pipeline (Orquestrador):** Persistência de métricas e redes coordenadas integrada ao final do ciclo.
- **Frontend (Diamond UI):** Dashboard dinâmico consumindo `dataService.js`, com suporte a sparklines e mapa geo-espacial.
- **Gating de Planos & UI:** Lógica de `planService` funcionando com modal de bloqueio injetado no HTML.
- **Integração de Pagamento:** Módulo `payments.js` implementado com suporte a checkout manual via PayPal (R$ 49,90). PIX desativado temporariamente por instrução.
- **Estratégia de Aquisição:** Página de Pricing implementada e versão de mapa embeddável (`embed/map.html`) criada para jornalismo de dados.

## 🚫 Abordagens Descartadas / Erros Conhecidos
- **[DESCARTADO] Conexão Direta Supabase no Frontend:** Inseguro (expõe chaves). Substituído por API Proxy.
- **[DESCARTADO] Cálculo de KPIs em Tempo Real na UI:** Muito lento com volume alto. Substituído por Views Materializadas e tabela `metricas_diarias`.
- **[CONHECIDO] Supabase CLI Local:** Não disponível no ambiente win32 atual. Scripts SQL devem ser gerados para execução manual/remota.

## 🐛 Bugs Atuais / Bloqueios
- **Dashboard sem Dados:** Resolvido na v19.1.1 com fallbacks na API. Se as novas views não existirem, o sistema usa as tabelas base.
- **Sincronização de Schema:** O script `diamond_schema_v1.sql` ainda deve ser aplicado no Supabase para habilitar 100% das features.
- **Solução Temporária:** Criado script `tools/seed_diamond.py` para popular dados de teste iniciais.
