# ROADMAP - Sentinela Democrática

## Status Atual: v19.6.0 (Munição Forense - Stripe & Credits) ✅
- **Munição Forense (STN)**: Sistema de tokens para monetização de dossiês e inteligência profunda.
- **Arquitetura Diamond**: Migração completa para API Proxy (FastAPI). O frontend não acessa mais o Supabase diretamente, garantindo segurança das chaves.
- **Gateway de Pagamento**: Integração total com Stripe Checkout e Webhooks para compra automatizada de pacotes STN.
- **Autenticação Real**: Fluxo de Login/Signup com Supabase Auth integrado à UI e ao sistema de créditos.

## Próximos Passos (v19.7.0)
- [ ] **Alertas Push**: Integração com Telegram Webhooks para notificações CRITICAL em tempo real.
- [ ] **Multi-Model IA**: Implementação de fallback Groq (Llama-3) + Gemini no `orquestrador.py`.
- [ ] **Monitoramento de Anúncios**: Expansão para a Meta Ad Library para detectar financiamento de desinformação.


---
*Atualizado em 29/04/2026 - Diamond Edition Growth concluída.*
