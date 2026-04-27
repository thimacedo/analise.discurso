import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Ajuste de path para o Vercel encontrar o modulo core
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.config import settings
from core.supabase_client import supabase

app = FastAPI(title="Sentinela API", version="16.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/v1/status")
async def status():
    return {
        "status": "online", 
        "version": "16.5.0", 
        "engine": "Diamond Unified",
        "db": supabase is not None
    }

@app.get("/api/v1/summary")
async def get_summary():
    if not supabase: return {"error": "DB disconnected"}
    res = supabase.table("candidatos").select("comentarios_totais_count, comentarios_odio_count").execute()
    total_a = sum(item.get('comentarios_totais_count', 0) for item in res.data)
    total_h = sum(item.get('comentarios_odio_count', 0) for item in res.data)
    return {
        "total_monitorados": len(res.data),
        "total_amostra": total_a,
        "total_alertas": total_h,
        "resiliencia": round(100 - ((total_h / total_a) * 100), 1) if total_a > 0 else 100.0
    }

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    if not supabase: return []
    res = supabase.table("candidatos").select("username, estado, comentarios_totais_count, comentarios_odio_count")\
        .gt("comentarios_totais_count", 0).order("comentarios_totais_count", desc=True).limit(10).execute()
    
    return [{
        "username": c['username'],
        "estado": c['estado'],
        "share_blindagem": round(100 - ((c.get('comentarios_odio_count', 0) / c.get('comentarios_totais_count', 1)) * 100), 2)
    } for c in res.data]
