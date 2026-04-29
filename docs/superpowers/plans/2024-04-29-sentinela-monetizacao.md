# Implementação Sentinela v19.6.0: Munição Forense (Tokens STN)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrar para um sistema de créditos (Tokens STN) para monetizar ações forenses profundas via Stripe.

**Architecture:** 
- **DB:** Supabase para saldo e histórico com RPC atômica.
- **Backend:** FastAPI como Proxy para Stripe Checkout e Webhooks.
- **Frontend:** UI reativa que consome créditos para gerar provas (PDF/Redes).

**Tech Stack:** FastAPI (Python), Stripe SDK, Supabase (PostgreSQL), Vanilla JS/CSS.

---

### Tarefa 1: Preparação do Banco de Dados (Supabase)

**Files:**
- Create: `scripts/migration_v19.6_stn.sql`

- [ ] **Passo 1: Criar o script SQL de migração**
```sql
-- scripts/migration_v19.6_stn.sql
-- 1. Colunas de saldo
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS stn_tokens INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS total_stn_spent INT DEFAULT 0;

-- 2. Tabela de Transações
CREATE TABLE IF NOT EXISTS public.stn_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE CASCADE NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('PURCHASE', 'CONSUMPTION', 'BONUS')),
    amount INT NOT NULL,
    stripe_session_id TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE public.stn_transactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own transactions" ON public.stn_transactions FOR SELECT USING (auth.uid() = user_id);

-- 3. RPC Atômica
CREATE OR REPLACE FUNCTION process_stn_transaction(
    p_user_id UUID,
    p_amount INT,
    p_type TEXT,
    p_session_id TEXT DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_current_balance INT;
BEGIN
    IF p_amount < 0 THEN
        SELECT stn_tokens INTO v_current_balance FROM public.profiles WHERE id = p_user_id FOR UPDATE;
        IF v_current_balance < ABS(p_amount) THEN
            RETURN FALSE;
        END IF;
    END IF;

    UPDATE public.profiles 
    SET 
        stn_tokens = stn_tokens + p_amount,
        total_stn_spent = CASE WHEN p_amount < 0 THEN total_stn_spent + ABS(p_amount) ELSE total_stn_spent END
    WHERE id = p_user_id;

    INSERT INTO public.stn_transactions (user_id, type, amount, stripe_session_id, metadata)
    VALUES (p_user_id, p_type, p_amount, p_session_id, p_metadata);

    RETURN TRUE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

- [ ] **Passo 2: Instruir execução no Supabase Dashboard** (Manual pelo usuário)

- [ ] **Passo 3: Commit do Script**
```bash
git add scripts/migration_v19.6_stn.sql
git commit -m "db: add STN tokens schema and atomic RPC"
```

---

### Tarefa 2: Backend - Integração Stripe (FastAPI)

**Files:**
- Modify: `api/index.py`
- Modify: `.env.local` (instrução)

- [ ] **Passo 1: Instalar dependência Stripe**
```bash
pip install stripe
```

- [ ] **Passo 2: Configurar endpoints de Checkout e Webhook**
```python
# api/index.py (adicionar ao final)
import stripe
from api.common import SUPABASE_URL, SUPABASE_KEY

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

PACKAGE_CONFIG = {
    "stn_starter": {"tokens": 1, "amount": 24900},
    "stn_squad":   {"tokens": 4, "amount": 59700},
    "stn_warroom": {"tokens": 15, "amount": 149700},
}

@app.post("/api/v1/checkout/create-session")
async def create_checkout_session(payload: dict = Body(...)):
    user_id = payload.get("user_id")
    package_slug = payload.get("package_slug")
    
    if package_slug not in PACKAGE_CONFIG:
        raise HTTPException(status_code=400, detail="Pacote invalido")

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card', 'pix'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {'name': f'Tokens STN - {package_slug}'},
                    'unit_amount': PACKAGE_CONFIG[package_slug]['amount'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{os.getenv('FRONTEND_URL')}/#monitor?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL')}/pricing.html",
            metadata={"user_id": user_id, "package_slug": package_slug}
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except Exception:
        return {"status": "invalid signature"}

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        pkg = session['metadata']['package_slug']
        
        # Chama RPC no Supabase via httpx
        from api.common import fetch_json
        await fetch_json(
            "rpc/process_stn_transaction",
            method="POST",
            json={
                "p_user_id": user_id,
                "p_amount": PACKAGE_CONFIG[pkg]['tokens'],
                "p_type": "PURCHASE",
                "p_session_id": session['id']
            }
        )
    return {"status": "success"}
```

- [ ] **Passo 3: Commit do Backend**
```bash
git add api/index.py
git commit -m "feat(api): implement stripe checkout and webhook for STN tokens"
```

---

### Tarefa 3: Frontend - Service de Créditos

**Files:**
- Modify: `src/services/authService.js`
- Modify: `src/core/payments.js`

- [ ] **Passo 1: Atualizar `getProfile` para carregar tokens**
```javascript
// src/services/authService.js
// No método getProfile(userId):
const { data, error } = await this.client
    .from('profiles')
    .select('*, stn_tokens') // Garante que stn_tokens vem no profile
    .eq('id', userId)
    .single();
```

- [ ] **Passo 2: Refatorar `initiatePayment` para Stripe**
```javascript
// src/core/payments.js
export async function initiateStripeCheckout(packageSlug) {
    const user = await authService.init();
    if (!user) {
        alert("Necessário login para adquirir tokens.");
        window.location.href = "/login.html"; // ou modal de auth
        return;
    }

    const resp = await fetch('/api/v1/checkout/create-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: user.id, package_slug: packageSlug })
    });
    
    const { url } = await resp.json();
    if (url) window.location.href = url;
}
```

- [ ] **Passo 3: Commit do Frontend Service**
```bash
git add src/services/authService.js src/core/payments.js
git commit -m "refactor(frontend): update auth and payment services for STN"
```

---

### Tarefa 4: UI/UX - Munição Forense no Dashboard

**Files:**
- Modify: `index.html`
- Modify: `src/core/ui.js`

- [ ] **Passo 1: Adicionar STN Counter no Header**
```html
<!-- index.html (dentro do brand-block ou sidebar-footer) -->
<div class="stn-badge glass-card" style="display:flex; align-items:center; gap:8px; padding:4px 12px; border-color:var(--accent);">
    <i data-lucide="zap" class="w-4 h-4 text-accent"></i>
    <span id="stn-balance" style="font-weight:800; font-family:'JetBrains Mono';">-- STN</span>
</div>
```

- [ ] **Passo 2: Lógica de Atualização do Saldo na UI**
```javascript
// src/core/ui.js
export function updateSTNUI() {
    const el = document.getElementById('stn-balance');
    if (el) {
        const tokens = authService.user?.stn_tokens || 0;
        el.innerText = `${tokens} STN`;
    }
}
```

- [ ] **Passo 3: Gating de Prova Forense (Botão Dossiê)**
```javascript
// No renderizador do Dossiê:
const btnLabel = (authService.user?.stn_tokens > 0) ? "⚡ Gerar Dossiê (1 STN)" : "🛒 Recarregar Munição";
const btnClass = (authService.user?.stn_tokens > 0) ? "cta-action" : "cta-upgrade";
// ... lógica do botão para chamar consumo ou pricing ...
```

- [ ] **Passo 4: Commit Final e Limpeza**
```bash
git add index.html src/core/ui.js
git commit -m "ui: implement STN counter and forensic action gating"
```
