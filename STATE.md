# Triagem de Estado e Pendências (Sentinela)

## 📊 Estado Geral (v20.5.2)
- **Operacional:** Sim. Fullstack Estável.
- **Backend/IA:** Integração Ollama (GGUF) unificada e com fallback inteligente. Latência rastreada.
- **Frontend/UI:** Diamond Edition ativa. KPIs com design semântico e robustez garantida (fallbacks de API via dataService).
- **Monetização:** AdSense injetado no feed (a cada 5 posts) e na sidebar direita.

## ✅ Concluído (v20.5.5)
- **STN-005: Diretório Global de Perfis**: Implementada interface de listagem e busca em tempo real para os 343+ candidatos monitorados, com cartões informativos premium, métricas de risco PASA e integração direta com o feed de análise.
- **Limpeza Linguística Diamond**: Removida terminologia restrita (perícia, forense, prova) da UI e APIs, substituindo por termos estratégicos como 'Análise', 'Créditos' e 'Dados'.
- **Correção de Falsos Positivos**: Implementada persistência real para descartes. O endpoint `/alerts/false-positive` agora possui tipagem rigorosa (Pydantic) e logs detalhados. O frontend utiliza o novo método `postJson` resiliente, garantindo que o descarte funcione tanto no Vercel quanto no Localhost via fallback automático.
- **Padronização de Escrita Resiliente**: Todos os fluxos de POST (descarte de alertas e geração de relatórios) foram migrados para o método `postJson` do `dataService`, que herda a inteligência de dupla tentativa (Vercel + Localhost).
- **Refatoração Implacável (Pickle Rick Mode)**: 
  - `api/index.py`: Eliminado boilerplate de erro, implementada Injeção de Dependência para Supabase, e externalizadas constantes PASA/Risco.
  - `src/services/dataService.js`: Lógica de fetch simplificada com helper assíncrono e retry robusto.
  - `src/core/app.js` & `src/services/authService.js`: Removida duplicação de configurações sensíveis, centralizando tudo em `src/config.js`.
- **Correção de Conectividade e KPIs**: Resolvido conflito de portas local (3000 vs 8000) via detecção dinâmica em `src/config.js`.
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
