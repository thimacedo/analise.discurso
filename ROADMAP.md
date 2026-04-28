# ROADMAP - Sentinela Democrática

## Status: v17.2.0 (Diamond Edition - Final UI Overhaul)
- **UI/UX**: Reestruturação completa do dashboard com foco em triagem operacional.
- **Alertas**: Implementação da trilha "Agressor ➔ Alvo" em tempo real.
- **Métricas**: Novo cálculo de "Taxa de Hostilidade" baseado em amostragem real (PASA %).
- **Mapa Geopolítico**: Finalizado com SVG de alta definição, heatmap dinâmico e Risk Pulse.
- **Filtros**: Sistema de isolamento de evidências por alvo funcional via ranking lateral.
- **Performance**: Otimização de renderização e remoção de restrições de rolagem (Overflow Fix).
- **Segurança**: 
  - Limpeza total do histórico Git (Secrets Removal).
  - (PENDENTE) Migração da `service_role` para Proxy API.

## Persistência Técnica (Contrato de Governança)
- [x] TOTP em `addalvo.html`.
- [x] Navegação SPA via hash (#).
- [x] Nomenclatura PASA (Sentinela) padronizada.
- [x] Fallback de mídia (onerror) garantido.

## Próximos Passos
- [ ] Implementar Proxy API (Node/Python) para ocultar chaves Supabase.
- [ ] Resolver conflito de Path no ambiente Python local.
- [ ] Ativar Worker Intel para processamento de backlog via Qwen Local.

---
*Atualizado em 28/04/2026*
