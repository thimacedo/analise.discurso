from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.supabase_client import supabase
from pydantic import BaseModel
from typing import Optional, List
import httpx
import time

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- ROTAS DE STATUS ---
@app.get("/api/v1/status")
async def status():
    return {
        "status": "online", 
        "version": settings.VERSION, 
        "protocol": "PASA v16.0",
        "db_connected": supabase is not None
    }

# --- ROTAS DO DASHBOARD ---
@app.get("/api/v1/candidatos")
async def get_candidatos():
    if not supabase: return []
    res = supabase.table("candidatos").select("*").eq("status_monitoramento", "Ativo").execute()
    return res.data

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    if not supabase: return []
    res = supabase.table("candidatos").select("username, estado, comentarios_totais_count, comentarios_odio_count")\
        .gt("comentarios_totais_count", 0).order("comentarios_totais_count", desc=True).limit(10).execute()
    
    processed = []
    for c in res.data:
        total = c.get('comentarios_totais_count', 1)
        odio = c.get('comentarios_odio_count', 0)
        processed.append({
            "username": c['username'],
            "estado": c['estado'],
            "share_blindagem": round(100 - ((odio / total) * 100), 2),
            "totais": total,
            "alertas": odio
        })
    return processed

# --- ROTAS DE INTELIGÃŠNCIA ---
@app.get("/api/v1/live-intelligence")
async def get_live_intelligence():
    if not supabase: return []
    res = supabase.table("comentarios").select("texto_bruto, candidato_id, is_hate")\
        .order("created_at", desc=True).limit(5).execute()
    return [{"alvo": c['candidato_id'], "texto": c['texto_bruto'], "is_hate": c['is_hate']} for c in res.data]

# --- ADMIN AUTH ---
class AuthRequest(BaseModel):
    code: str

@app.post("/api/v1/admin/auth/verify")
async def verify_totp(request: AuthRequest):
    if not settings.ADMIN_TOTP_SECRET:
        raise HTTPException(status_code=500, detail="TOTP nao configurado.")
    # Implementacao de verificacao real aqui se pyotp disponivel
    return {"status": "success", "token": "admin-session-active"}

