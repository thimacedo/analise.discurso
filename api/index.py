import os
import asyncio
import httpx
import json
import io
import base64
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import stripe
import segno
import pyotp
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS ultra-permissivo para debug local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

class AuthRequest(BaseModel):
    code: str

class TargetUpsertRequest(BaseModel):
    username: str
    nome_completo: Optional[str] = "Não informado"
    cargo: Optional[str] = "Monitorado"
    estado: Optional[str] = "BR"
    status: Optional[str] = "Ativo"

# --- ROTAS DE STATUS ---
@app.get("/api/v1/status")
@app.get("/api/status")
async def status():
    return {"status": "online", "database": "connected", "version": "15.5.2"}

# --- ROTAS ADMIN ---
@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    with open("addalvo.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/v1/admin/auth/verify")
async def verify_totp(request: AuthRequest):
    secret = os.getenv("SENTINELA_ADMIN_TOTP_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Segredo TOTP não configurado.")
    totp = pyotp.TOTP(secret.strip())
    clean_code = request.code.replace(" ", "").strip()
    if totp.verify(clean_code):
        return {"status": "success", "token": "admin-session-active"}
    raise HTTPException(status_code=401, detail="Código inválido.")

@app.get("/api/v1/admin/targets")
async def list_targets_api(search: Optional[str] = None):
    url = f"{SUPABASE_URL}/rest/v1/candidatos?select=*"
    if search:
        url += f"&or=(username.ilike.*{search}*,nome_completo.ilike.*{search}*)"
    
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=get_supabase_headers())
        targets = res.json() if res.status_code == 200 else []
        for t in targets:
            t['status'] = t.get('status_monitoramento', 'Ativo')
        return targets

@app.get("/api/v1/admin/targets/template")
async def download_template():
    df = pd.DataFrame(columns=['username', 'full_name', 'cargo', 'estado', 'status'])
    df.loc[0] = ['lulaoficial', 'Luiz Inácio Lula da Silva', 'Presidente', 'BR', 'Ativo']
    output = io.StringIO()
    df.to_csv(output, index=False)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=modelo_sentinela.csv"}
    )

@app.patch("/api/v1/admin/targets/{username}/status")
async def update_status_api(username: str, status: str):
    url = f"{SUPABASE_URL}/rest/v1/candidatos?username=eq.{username.lower()}"
    async with httpx.AsyncClient() as client:
        res = await client.patch(url, headers=get_supabase_headers(), json={"status_monitoramento": status})
        return {"status": "success", "code": res.status_code}

@app.post("/api/v1/admin/targets/upsert")
async def upsert_target_api(target: TargetUpsertRequest):
    username = target.username.strip().replace("@", "").lower()
    data = {
        "username": username,
        "nome_completo": target.nome_completo,
        "cargo": target.cargo,
        "estado": target.estado,
        "status_monitoramento": target.status
    }
    headers = get_supabase_headers()
    headers["Prefer"] = "resolution=merge-duplicates"
    async with httpx.AsyncClient() as client:
        await client.post(f"{SUPABASE_URL}/rest/v1/candidatos", headers=headers, json=data)
        return {"status": "success"}

# Rota raiz
@app.get("/")
async def root():
    return {"message": "Sentinela Intelligence API", "admin": "/admin"}
