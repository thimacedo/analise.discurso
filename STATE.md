# Triagem de Estado e Pendências (Sentinela)

## 📊 Estado Geral (v20.5.2)
- **Operacional:** Sim. Fullstack Estável.
- **Backend/IA:** Integração Ollama (GGUF) unificada e com fallback inteligente. Latência rastreada.
- **Frontend/UI:** Diamond Edition ativa. KPIs com design semântico e robustez garantida (fallbacks de API via dataService).
- **Monetização:** AdSense injetado no feed (a cada 5 posts) e na sidebar direita.

## ✅ Concluído (v20.5.4)
- **Refatoração Implacável (Pickle Rick Mode)**: 
  - `api/index.py`: Eliminado boilerplate de erro, implementada Injeção de Dependência para Supabase, e externalizadas constantes PASA/Risco.
  - `src/services/dataService.js`: Lógica de fetch simplificada com helper assíncrono e retry robusto.
  - `src/core/app.js` & `src/services/authService.js`: Removida duplicação de configurações sensíveis, centralizando tudo em `src/config.js`.
- **Correção de Conectividade e KPIs**: Resolvido conflito de portas local (3000 vs 8000) via detecção dinâmica em `src/config.js`.
- **STN-001: Repositório de Dossiês Forenses**: Implementada infraestrutura de persistência estruturada no Supabase com hash de integridade SHA-256 e metadados forenses automáticos.
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
