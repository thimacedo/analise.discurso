# Triagem de Estado e Pendências (Sentinela)

## 📊 Estado Geral (v20.5.1)
- **Operacional:** Sim. Fullstack Estável.
- **Backend/IA:** Integração Ollama (GGUF) unificada e com fallback inteligente. Latência rastreada.
- **Frontend/UI:** Diamond Edition ativa. KPIs com design semântico e robustez garantida (fallbacks de API via dataService).
- **Monetização:** AdSense injetado no feed (a cada 5 posts) e na sidebar direita.

## ⚠️ Pendências Críticas
- [ ] Integração Meta Ad Library (Epico STN-003) - Monitoramento de anúncios pagos.
- [ ] Diretório Global de Perfis, Repositório de Dossiês Forenses, Geopolítica UF - Mapa Integrado, Filtros de Inteligência

## 🛠 Plano de Ação (Resumido)
1. **STN-003.1:** Implementar `core/meta_ad_service.py` para busca na API da Meta.
2. **STN-003.2:** Persistência de anúncios no Supabase via `DatabaseClient`.
3. **STN-003.3:** Classificação PASA v16.4 para anúncios detectados.


---
*Estado: Arquitetura Diamond consolidada, testada E2E e monetizada.*
