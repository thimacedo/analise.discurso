# Triagem de Estado e Pendências (Sentinela)

## 📊 Estado Geral (v20.5.2)
- **Operacional:** Sim. Fullstack Estável.
- **Backend/IA:** Integração Ollama (GGUF) unificada e com fallback inteligente. Latência rastreada.
- **Frontend/UI:** Diamond Edition ativa. KPIs com design semântico e robustez garantida (fallbacks de API via dataService).
- **Monetização:** AdSense injetado no feed (a cada 5 posts) e na sidebar direita.

## ✅ Concluído (v20.5.6)
- **STN-003: Meta Ad Library**: Implementado painel de monitoramento de anúncios pagos com integração ao motor de inteligência e links diretos para a biblioteca oficial.
- **STN-007: Refatoração AIService**: Motor de inteligência consolidado com arquitetura de cascata resiliente e logs de telemetria integrados.
- **STN-006: Geopolítica UF**: Mapa vetorial interativo D3-style integrado com ranking de hostilidade por estado em tempo real.
- **STN-005: Diretório Global de Perfis**: Interface premium de perfis com busca e métricas PASA integradas.
- **Limpeza Linguística Diamond**: Removida terminologia restrita da UI/API.
- **STN-001: Repositório de Relatórios Estratégicos**: Implementada infraestrutura de persistência estruturada no Supabase com hash de integridade SHA-256 e metadados estratégicos automáticos.
- **Integração Meta Ad Library (Epico STN-003)**: Monitoramento de anúncios pagos via API oficial (Ads Archive).
  - Implementado `core/meta_ad_service.py` com busca assíncrona e normalização.
  - Implementado `processing/ad_processor.py` com classificação PASA v16.4.
  - Persistência em lote no Supabase via `DatabaseClient`.

## ⚠️ Pendências Críticas
- [ ] Diretório Global de Perfis, Repositório de Dossiês Forenses, Geopolítica UF - Mapa Integrado, Filtros de Inteligência

## 🛠 Plano de Ação (Resumido)
1. **STN-003.1:** Implementar `core/meta_ad_service.py` para busca na API da Meta.
2. **STN-003.2:** Persistência de anúncios no Supabase via `DatabaseClient`.
3. **STN-003.3:** Classificação PASA v16.4 para anúncios detectados.


---
*Estado: Arquitetura Diamond consolidada, testada E2E e monetizada.*
