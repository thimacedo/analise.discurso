# ROADMAP - Sentinela Democrática

## Status Atual: v19.1.0 (Diamond Edition - UI & Growth) ✅
- **Arquitetura Diamond**: Migração completa para API Proxy (FastAPI). O frontend não acessa mais o Supabase diretamente, garantindo segurança das chaves.
- **Enriquecimento de Dados**: Implementada persistência de `metricas_diarias`, `redes_coordenadas` e `alertas_ativos`.
- **Inteligência de Redes**: `DataMiner` agora persiste clusters e detecta picos de hostilidade (Z-Score) automaticamente.
- **UI Dynamic**: Dashboard 100% dinâmico com sparklines, tendências semanais, categorias PASA e mapa geopolítico real.
- **Monetização e Aquisição**: Modal de gating de acesso, página de Preços (`pricing.html`) criados e Mapa Inteligente em modo embed (`embed/map.html`) configurado para escala viral.

## Próximos Passos (v19.5.0)
- [ ] **Gateway de Pagamento**: Integração com Stripe/Asaas para checkout direto dos planos Pro/Enterprise na página de pricing.
- [ ] **Autenticação de Usuários**: Fluxo de Login/Signup com Supabase Auth integrado à UI para validar o perfil real em substituição ao mock atual do `SENTINELA_USER`.
- [ ] **Alertas Push**: Integração com Telegram Webhooks para notificações CRITICAL em tempo real.
- [ ] **Multi-Model IA**: Implementação de fallback Groq (Llama-3) no `orquestrador.py`.

---
*Atualizado em 29/04/2026 - Diamond Edition Growth concluída.*
