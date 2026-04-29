# Especificação Técnica: Sentinela v19.6.0 - Sistema de "Munição Forense" (Tokens STN)

**Data:** 29 de abril de 2026  
**Status:** Aprovado para Implementação  
**Versão:** 19.6.0  

## 1. Visão Geral
Migração do modelo de assinatura manual (PayPal) para um sistema transacional de **Créditos de Inteligência (Tokens STN)**, codinome "Munição Forense". O usuário compra tokens para realizar ações de alta profundidade (geração de PDF, rastreamento de redes), enquanto a transparência do dashboard permanece pública.

## 2. Modelo de Dados (Supabase)

### 2.1 Alterações em Tabelas Existentes
- **Tabela `profiles`**:
    - `stn_tokens` (int4, default: 0): Saldo atual de munição forense.
    - `total_stn_spent` (int4, default: 0): Acumulado histórico para métricas de LTV.

### 2.2 Novas Tabelas
- **Tabela `stn_transactions`**:
    - `id` (uuid, primary key)
    - `user_id` (uuid, references profiles.id)
    - `type` (text): 'PURCHASE', 'CONSUMPTION', 'BONUS'
    - `amount` (int4): Quantidade de tokens (+ ou -)
    - `stripe_session_id` (text, nullable): Link com a transação financeira
    - `metadata` (jsonb): Detalhes da ação (ex: `{"target": "@username", "action": "pdf_gen"}`)
    - `created_at` (timestamptz, default: now())

### 2.3 Lógica Atômica (Stored Procedure)
Criar RPC `process_stn_transaction(p_user_id, p_amount, p_type, p_session_id, p_metadata)` para garantir que o saldo e o histórico sejam atualizados em uma única transação SQL, evitando inconsistências.

## 3. Integração Financeira (Stripe)

### 3.1 Pacotes de Preço
| Pacote | Slug | Tokens | Bônus | Total | Preço |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Starter | `stn_starter` | 1 | 0 | 1 | R$ 249,00 |
| Squad | `stn_squad` | 3 | 1 | 4 | R$ 597,00 |
| War Room | `stn_warroom` | 10 | 5 | 15 | R$ 1.497,00 |

### 3.2 Endpoints FastAPI (`api/index.py`)
- `POST /api/v1/checkout/create-session`:
    - Valida token Supabase do usuário.
    - Chama Stripe API para criar sessão de checkout.
    - Metadata: `user_id`, `package_slug`.
- `POST /api/v1/webhooks/stripe`:
    - Verifica assinatura `whsec_...`.
    - Evento `checkout.session.completed`: Dispara a RPC de crédito de tokens.

## 4. Interface e Experiência (UI/UX)

### 4.1 Componentes Novos
- **STN Counter (Header)**: Exibição persistente do saldo: `[ ⚡ 5 STN ]`.
- **Botão de Ação (Dossiê)**: "Gerar Dossiê Forense (1 STN)".
- **Modal de Recarga**: Exibição dos 3 pacotes com visual de "loja de itens" (estética Diamond).

### 4.2 Gating de Funcionalidade
O frontend deve verificar `state.profile.stn_tokens` antes de habilitar as rotas de download de PDF ou análise profunda de redes.

## 5. Estratégia de Implementação
1. **Fase 1**: Atualização do Schema SQL e RPCs no Supabase.
2. **Fase 2**: Implementação dos endpoints de Checkout e Webhook no FastAPI.
3. **Fase 3**: Atualização do `src/services/authService.js` para ler os tokens no login.
4. **Fase 4**: Redesenho da `pricing.html` e botões de ação no dashboard.

## 6. Critérios de Aceite
- O usuário deve receber os tokens automaticamente em até 10 segundos após o pagamento.
- O sistema deve impedir o consumo se o saldo for zero.
- Cada transação deve estar registrada na tabela `stn_transactions`.
