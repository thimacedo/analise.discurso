from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.supabase_client import supabase
from pydantic import BaseModel
from typing import List
import time

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/v1/status")
async def status():
    return {"status": "online", "version": "16.2.0", "db": supabase is not None}

@app.get("/api/v1/candidatos")
async def get_candidatos():
    if not supabase: return []
    try:
        res = supabase.table("candidatos").select("*").eq("status_monitoramento", "Ativo").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/alertas")
async def get_alertas(limit: int = 10):
    if not supabase: return []
    try:
        res = supabase.table("comentarios").select("texto_bruto, candidato_id, is_hate")\
            .eq("is_hate", True).order("created_at", desc=True).limit(limit).execute()
        return [{"alvo": c['candidato_id'], "texto": c['texto_bruto'], "is_hate": c['is_hate']} for c in res.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/summary")
async def get_summary():
    if not supabase: return {"total_amostra": 0, "total_alertas": 0, "total_monitorados": 0}
    try:
        c_res = supabase.table("candidatos").select("comentarios_totais_count, comentarios_odio_count").execute()
        total_m = len(c_res.data)
        total_a = sum(item.get('comentarios_totais_count', 0) for item in c_res.data)
        total_h = sum(item.get('comentarios_odio_count', 0) for item in c_res.data)
        return {
            "total_monitorados": total_m,
            "total_amostra": total_a,
            "total_alertas": total_h,
            "resiliencia": round(100 - ((total_h / total_a) * 100), 1) if total_a > 0 else 100.0
        }
    except: return {"total_amostra": 0, "total_alertas": 0, "total_monitorados": 0}

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    if not supabase: return []
    try:
        res = supabase.table("candidatos").select("username, estado, comentarios_totais_count, comentarios_odio_count")\
            .gt("comentarios_totais_count", 0).order("comentarios_totais_count", desc=True).limit(10).execute()
        return [{
            "username": c['username'],
            "estado": c['estado'],
            "share_blindagem": round(100 - ((c.get('comentarios_odio_count', 0) / c.get('comentarios_totais_count', 1)) * 100), 2)
        } for c in res.data]
    except: return []
