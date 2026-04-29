# ROADMAP - Sentinela Democrática

## Status Atual: v19.0.0 (Diamond Edition Foundations) ✅
- **Arquitetura Diamond**: Migração completa para API Proxy (FastAPI). O frontend não acessa mais o Supabase diretamente, garantindo segurança das chaves.
- **Enriquecimento de Dados**: Implementada persistência de `metricas_diarias`, `redes_coordenadas` e `alertas_ativos`.
- **Inteligência de Redes**: `DataMiner` agora persiste clusters e detecta picos de hostilidade (Z-Score) automaticamente.
- **UI Dynamic**: Dashboard 100% dinâmico com sparklines, tendências semanais, categorias PASA e mapa geopolítico real.
- **Plano de Gating**: Implementada lógica de `planService` (Public/Pro/Enterprise) para monetização.

## Próximos Passos (v19.5.0)
- [ ] **Monetização Real**: Integração com Stripe/Asaas para automação de planos Pro/Enterprise.
- [ ] **Alertas Push**: Integração com Telegram Webhooks para notificações CRITICAL em tempo real.
- [ ] **Multi-Model IA**: Implementação de fallback Groq (Llama-3) no `orquestrador.py`.
- [ ] **Exportação Avançada**: Geração de relatórios CSV/JSON para usuários Enterprise.

---
*Atualizado em 29/04/2026 - Diamond Edition Foundations concluída.*
