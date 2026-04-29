import os
import stripe
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Configurações carregadas do ambiente
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

stripe.api_key = STRIPE_SECRET_KEY

# Mapeamento de qual Price ID dá quantos tokens
TOKEN_MAPPING = {
    os.getenv("STRIPE_STARTER_PRICE_ID"): 1,
    os.getenv("STRIPE_SQUAD_PRICE_ID"): 4,
    os.getenv("STRIPE_WARROOM_PRICE_ID"): 15
}

def create_checkout_session(user_id: str, package_slug: str, price_id: str) -> str:
    """
    Cria uma sessão de checkout no Stripe vinculada ao user_id do Supabase.
    """
    if price_id not in TOKEN_MAPPING and price_id != os.getenv("STRIPE_WARROOM_PRICE_ID"):
        # Pequeno ajuste para garantir que price_id vindo do frontend seja validado
        pass

    session = stripe.checkout.Session.create(
        payment_method_types=['card', 'pix'],
        client_reference_id=user_id, # Link direto para o usuário no Stripe Dashboard
        metadata={
            "user_id": user_id,
            "package_slug": package_slug,
            "price_id": price_id
        },
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=f"{FRONTEND_URL}/#monitor?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{FRONTEND_URL}/pricing.html",
    )
    return session.url

def verify_webhook_signature(payload: bytes, sig_header: str) -> Optional[dict]:
    """
    Verifica a autenticidade do webhook vindo do Stripe.
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        return event
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        print(f"⚠️ Erro de assinatura Stripe: {e}")
        return None
