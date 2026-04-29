# ROADMAP - Sentinela Democrática

## Status Atual: v19.7.1 (Intelligent Monitoring Locked) ✅

- **Monitoramento Inteligente (TargetManager)**: Implementado filtro de deduplicação e raspagem recente (48h), otimizando recursos de rede e API.
- **Persistência Forense Ativa**: O Orquestrador grava os resultados da IA (Categoria e Confiança Float) diretamente no Supabase em tempo real.
- **Calibração PASA v16.4**: Blindagem contra falsos positivos implementada.
- **Monetização (STN)**: Stripe integrado. Sistema de créditos via RPC atômica funcional.
- **Resiliência IA**: Backoff Exponencial para tratamento de Rate Limits da API Groq.
- **Alertas de Inteligência**: Resumo de mineração enviado automaticamente via WhatsApp (CallMeBot).

## Próximos Passos (v20.0 - Escala e Expansão)

- [ ] **Meta Ad Library**: Iniciar integração com a biblioteca de anúncios do Facebook/Instagram para rastrear financiamento de desinformação.
- [ ] **Firebase Push Notifications**: Migrar alertas de WhatsApp (CallMeBot) para um sistema de Notificações Push nativo no Dashboard (In-App) via Firebase Cloud Messaging.
- [ ] **Multi-Model Fallback**: Adicionar OpenAI/Gemini como fallback secundário caso o Ollama local e o Groq falhem simultaneamente.

---
*Atualizado em 29/04/2026 - Diamond Edition Persistence & Alerting concluída.*
