# Estado Atual do Sistema - SENTINELA | Diamond Edition

## 💎 Versão: 19.6.0 (Munição Forense)

- **Data da última atualização:** 29/04/2026
- **Status:** Sistema de Créditos de Inteligência (Tokens STN) operacional. Integração Stripe (Checkout/Webhook) concluída e funcional.

## ✅ O que está funcionando

- **Munição Forense (STN):** Sistema de créditos para ações forenses profundas. Saldo persistente no Supabase.
- **Integração Stripe (Locked):** Geração de sessões de checkout e processamento de webhooks para compra de tokens (Starter, Squad, War Room).
- **Consumo Atômico:** RPC `process_stn_transaction` garante integridade de saldo e histórico de auditoria.
- **Interface Gamificada:** Contador de tokens no header e gating de "Gerar Dossiê" nos cards.
- **Autenticação Real (Locked):** Fluxo de Login/Signup via Supabase Auth totalmente integrado aos créditos.
- **Integridade de Dados (Locked):** Pipeline Scrapy -> Supabase agora envia payload completo (timestamp e engajamento).
- **Automação (v19.6.1):** Pipeline GitHub Actions corrigida (requirements, segredos e caminhos de assets). Geração de CSV para API integrada ao orquestrador.

## 🚫 Abordagens Descartadas

- **[DESCARTADO] Classificação PASA em tempo real no Dashboard:** Inviável.
- **[DESCARTADO] Chaves de API no Frontend:** Inseguro.

## 🚀 Próximo Passo

- Iniciar v19.7.0: Implementação do Fallback Multi-Model (Groq Llama-3 + Gemini) no Orquestrador para resiliência de cota.
