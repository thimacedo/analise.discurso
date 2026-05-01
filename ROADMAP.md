# ROADMAP - Sentinela Democrática

## Status Atual: v19.8.0 (Ruthless Architecture & Unified Core) ✅

- **Arquitetura Unificada Diamond**: Toda a lógica de persistência e inteligência foi consolidada em `core/db.py` e `core/ai_service.py`, eliminando +500 linhas de código redundante.
- **Async Pipeline**: O orquestrador agora opera de forma totalmente assíncrona, com batch updates para performance máxima.
- **Híbrido de IA Resiliente**: Fallback automático entre Gemini, Groq e Ollama Local integrado nativamente no serviço de IA.
- **Segurança de Subprocesso**: Removido uso de `shell=True` nas chamadas de sistema do orquestrador.
- **Métricas Forenses**: Persistência de clusters e redes coordenadas otimizada via batching.


## Próximos Passos (v20.0 - Escala e Expansão)

- [ ] **Meta Ad Library**: Iniciar integração com a biblioteca de anúncios do Facebook/Instagram para rastrear financiamento de desinformação.
- [ ] **Firebase Push Notifications**: Migrar alertas de WhatsApp (CallMeBot) para um sistema de Notificações Push nativo no Dashboard (In-App) via Firebase Cloud Messaging.
- [x] **Multi-Model Fallback**: Adicionado modo Híbrido com suporte ao Gemini para complementar o Ollama (`qwen2.5:3b`) local.

---
*Atualizado em 30/04/2026 - Qwen Local Coder e Modo Híbrido (Gemini) integrados.*
