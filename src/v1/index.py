import os
import asyncio
import httpx
import time
import json
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, PlainTextResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe
import segno
import io
import base64
import pyotp
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURAÇÃO ---
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
stripe.api_key = STRIPE_SECRET_KEY
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

PRODUCT_PRICE = 4999 # R$ 49,99 em centavos
PIX_PAYLOAD = "00020126580014br.gov.bcb.pix0136sentinela-pay-1827611269042960520400005303986540549.995802BR5913SENTINELA INC6008BRASILIA62070503***6304E21D"

# --- HELPERS ---
def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# --- SCHEMAS ---
class AuthRequest(BaseModel):
    code: str

class TargetUpsertRequest(BaseModel):
    username: str
    nome_completo: Optional[str] = "Não informado"
    cargo: Optional[str] = "Monitorado"
    estado: Optional[str] = "BR"
    status: Optional[str] = "Ativo"

# --- ROTAS PÚBLICAS ---

@app.get("/api/status")
@app.get("/api/v1/status")
async def status():
    return {"status": "online", "engine": "Groq Llama 3.3", "database": "connected", "version": "15.5.0"}

@app.post("/api/create-checkout-session")
async def create_checkout_session(request: Request):
    try:
        origin = request.headers.get("origin") or "https://sentinela.politica.digital"
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
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
        return JSONResponse({"error": str(e)}, status_code=400)

@app.get("/api/generate-pix")
async def generate_pix():
    try:
        qr = segno.make(PIX_PAYLOAD)
        out = io.BytesIO()
        qr.save(out, kind='png', scale=10, dark='#020617', light='#ffffff')
        img_str = base64.b64encode(out.getvalue()).decode()
        return {"qr_code": f"data:image/png;base64,{img_str}", "payload": PIX_PAYLOAD, "amount": 49.99}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# --- ROTAS ADMIN (TOTP) ---

@app.post("/api/v1/admin/auth/verify")
async def verify_totp(request: AuthRequest):
    secret = os.getenv("SENTINELA_ADMIN_TOTP_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Segredo TOTP não configurado.")
    totp = pyotp.TOTP(secret)
    if totp.verify(request.code.replace(" ", "")):
        return {"status": "success", "token": "admin-session-active"}
    raise HTTPException(status_code=401, detail="Código inválido.")

@app.get("/api/v1/admin/targets")
async def list_targets(search: Optional[str] = None):
    url = f"{SUPABASE_URL}/rest/v1/candidatos?select=*"
    if search:
        url += f"&or=(username.ilike.*{search}*,nome_completo.ilike.*{search}*)"
    
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=get_supabase_headers())
        if res.status_code != 200:
            return []
        targets = res.json()
        return [
            {
                "username": t['username'],
                "nome_completo": t['nome_completo'],
                "cargo": t['cargo'],
                "estado": t['estado'],
                "status": t['status_monitoramento']
            } for t in targets
        ]

@app.post("/api/v1/admin/targets/upsert")
async def upsert_target(target: TargetUpsertRequest):
    username = target.username.strip().replace("@", "").lower()
    data = {
        "username": username,
        "nome_completo": target.nome_completo,
        "cargo": target.cargo,
        "estado": target.estado,
        "status_monitoramento": target.status
    }
    url = f"{SUPABASE_URL}/rest/v1/candidatos"
    headers = get_supabase_headers()
    headers["Prefer"] = "resolution=merge-duplicates"
    
    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, json=data)
        if res.status_code not in [200, 201]:
            raise HTTPException(status_code=400, detail=res.text)
        return {"status": "success"}

@app.patch("/api/v1/admin/targets/{username}/status")
async def update_status(username: str, status: str):
    url = f"{SUPABASE_URL}/rest/v1/candidatos?username=eq.{username.lower()}"
    async with httpx.AsyncClient() as client:
        res = await client.patch(url, headers=get_supabase_headers(), json={"status_monitoramento": status})
        return {"status": "success"}
