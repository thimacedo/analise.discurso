import os
import asyncio
import httpx
import time
import json
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from groq import Groq
import stripe
import segno
import io
import base64

app = FastAPI()

# --- CONFIGURAÇÃO ---
# Prioriza chaves live para produção
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY

# Valor unificado v15.1
PRODUCT_PRICE = 4999 # R$ 49,99 em centavos
PIX_PAYLOAD = "00020126580014br.gov.bcb.pix0136sentinela-pay-1827611269042960520400005303986540549.995802BR5913SENTINELA INC6008BRASILIA62070503***6304E21D"

@app.get("/api/status")
async def status():
    return {"status": "online", "engine": "Groq Llama 3.3", "billing": "Stripe/PayPal/PIX", "price": 49.99}

@app.post("/api/create-checkout-session")
async def create_checkout_session(request: Request):
    try:
        origin = request.headers.get("origin") or "https://sentinela.politica.digital"
        
        # Correção: Adicionado payment_method_configuration se necessário, mas simplificando para garantir sucesso
        session = stripe.checkout.Session.create(
            payment_method_types=['card'], # Removido 'pix' aqui para evitar conflito com payload manual se der erro
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': 'Dossiê Sentinela v15 - Relatório Profundo',
                        'description': 'Acesso total à inteligência situacional e preditiva.',
                    },
                    'unit_amount': PRODUCT_PRICE,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{origin}/complete.html?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{origin}/index.html#dossie",
        )
        return JSONResponse({"url": session.url})
    except Exception as e:
        print(f"Stripe Error Detail: {str(e)}")
        return JSONResponse({"error": "Gateway temporariamente indisponível. Tente PIX ou PayPal."}, status_code=400)

@app.get("/api/generate-pix")
async def generate_pix():
    try:
        # Gera QR Code estático do PIX
        qr = segno.make(PIX_PAYLOAD)
        out = io.BytesIO()
        qr.save(out, kind='png', scale=10, dark='#020617', light='#ffffff')
        img_str = base64.b64encode(out.getvalue()).decode()
        
        return {
            "qr_code": f"data:image/png;base64,{img_str}",
            "payload": PIX_PAYLOAD,
            "amount": 49.99
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/session-status")
async def session_status(session_id: str):
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {"status": session.status, "payment_status": session.payment_status}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
