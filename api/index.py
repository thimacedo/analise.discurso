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
from fastapi.staticfiles import StaticFiles
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

# Servir arquivos estáticos (CSS, JS, Imagens)
if os.path.exists("src"):
    app.mount("/src", StaticFiles(directory="src"), name="src")
if os.path.exists("docs"):
    app.mount("/docs", StaticFiles(directory="docs"), name="docs")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# --- ROTAS DE SERVIÇO DE PÁGINAS ---

@app.get("/", response_class=HTMLResponse)
async def home_page():
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content, media_type="text/html; charset=utf-8")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page():
    with open("addalvo.html", "r", encoding="utf-8") as f:
        content = f.read()
    return HTMLResponse(content=content, media_type="text/html; charset=utf-8")

# --- ROTAS DE API ---

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,estado,comentarios_totais_count,comentarios_odio_count&status_monitoramento=ilike.Ativo&order=comentarios_totais_count.desc&limit=10"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=get_supabase_headers())
        if res.status_code != 200:
            return []
        
        data = res.json()
        processed = []
        for c in data:
            total = c.get('comentarios_totais_count') or 0
            odio = c.get('comentarios_odio_count') or 0
            blindagem = 100.0
            if total > 0:
                blindagem = 100 - ((odio / total) * 100)
            
            processed.append({
                "username": c['username'],
                "estado": c['estado'],
                "share_blindagem": round(blindagem, 2)
            })
        return processed

@app.get("/api/v1/status")
@app.get("/api/status")
async def status():
    return {"status": "online", "database": "connected", "version": "15.6.2"}

@app.post("/api/v1/admin/auth/verify")
async def verify_totp(request: dict):
    secret = os.getenv("SENTINELA_ADMIN_TOTP_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Segredo TOTP não configurado.")
    totp = pyotp.TOTP(secret.strip())
    code = request.get("code", "").replace(" ", "").strip()
    if totp.verify(code):
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

@app.get("/")
async def root():
    return {"message": "Sentinela Intelligence API", "status": "Online"}
