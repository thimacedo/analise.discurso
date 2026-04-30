# ROADMAP - Sentinela Democrática

## Status Atual: v19.7.5 (Hybrid AI & Qwen Local Coder) ✅

- **Arquitetura Híbrida de Auth**: Reintegrado SDK Supabase exclusivamente para gestão de sessão, mantendo a integridade do Proxy FastAPI para dados.
- **Segurança de Infraestrutura**: Removido arquivo `.github/workflows/render.yaml` que continha credenciais expostas e causava erro de execução no GitHub Actions.
- **CI/CD Operacional**: Implementado workflow real de deploy em `.github/workflows/render_deploy.yml`.
- **Monitoramento Inteligente (TargetManager)**: Implementado filtro de deduplicação e raspagem recente (48h), otimizando recursos de rede e API.
- **Persistência Forense Ativa**: O Orquestrador grava os resultados da IA (Categoria e Confiança Float) diretamente no Supabase em tempo real.
- **Calibração PASA v16.4**: Blindagem contra falsos positivos implementada.
- **Integração de IA Local e Híbrida**: O modelo `qwen2.5:3b` foi adotado como o motor local padrão, e foi estabelecida integração com o Gemini como alternativa na nuvem via variável `IA_PROVIDER`.
- **Monetização (STN)**: Stripe integrado. Sistema de créditos via RPC atômica funcional.
- **Resiliência IA**: Backoff Exponencial para tratamento de Rate Limits da API Groq.
- **Alertas de Inteligência**: Resumo de mineração enviado automaticamente via WhatsApp (CallMeBot).

## Próximos Passos (v20.0 - Escala e Expansão)

- [ ] **Meta Ad Library**: Iniciar integração com a biblioteca de anúncios do Facebook/Instagram para rastrear financiamento de desinformação.
- [ ] **Firebase Push Notifications**: Migrar alertas de WhatsApp (CallMeBot) para um sistema de Notificações Push nativo no Dashboard (In-App) via Firebase Cloud Messaging.
- [x] **Multi-Model Fallback**: Adicionado modo Híbrido com suporte ao Gemini para complementar o Ollama (`qwen2.5:3b`) local.

---
*Atualizado em 30/04/2026 - Qwen Local Coder e Modo Híbrido (Gemini) integrados.*
