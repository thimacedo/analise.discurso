# ROADMAP - Sentinela Democrática

## Status Atual: v20.5.1 (Diamond Stability) ✅

- **Arquitetura Visual**: Frontend reestruturado com ícones Lucide, gradientes semânticos, avatares duplos e algoritmo de feed misto.
- **Resiliência UI**: Dados fallback injetados no `dataService.js` e cálculos de emergência no cliente para prevenir travamentos por timeouts da API.
- **Monetização**: AdSense injetado no Feed e na Sidebar.
- **Backend de IA**: Orquestrador migrado para suporte nativo e rastreado do Ollama (modelos GGUF locais), reduzindo custos e dependência da nuvem.
- **Testes**: Suite Playwright de roteamento E2E validada.

## Próximos Passos (v20.6)

- [ ] **Monitoramento de Monetização**: Validar conversões e cliques no AdSense In-Feed.
- [ ] **Escalabilidade**: Estudar viabilidade de filas com Celery/Redis caso o banco cresça excessivamente.

---
*Atualizado em 02/05/2026 - v20.5.1 estabilizada, documentada e comutada.*
