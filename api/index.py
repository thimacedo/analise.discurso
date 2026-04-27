from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.supabase_client import supabase
from pydantic import BaseModel
from typing import List, dict
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
    return {"status": "online", "version": "16.1.0", "db": supabase is not None}

@app.get("/api/v1/summary")
async def get_summary():
    """Retorna os KPIs consolidados para o Dashboard"""
    if not supabase: return {"total_amostra": 0, "total_alertas": 0, "total_monitorados": 0}
    
    # 1. Total de Monitorados
    c_res = supabase.table("candidatos").select("id", count="exact").eq("status_monitoramento", "Ativo").execute()
    total_m = c_res.count or 0
    
    # 2. Amostragem Total (Soma de todos os comentarios)
    sum_res = supabase.table("candidatos").select("comentarios_totais_count, comentarios_odio_count").execute()
    total_a = sum(item.get('comentarios_totais_count', 0) for item in sum_res.data)
    total_h = sum(item.get('comentarios_odio_count', 0) for item in sum_res.data)
    
    return {
        "total_monitorados": total_m,
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

@app.get("/api/v1/geopolitica")
async def get_geopolitica():
    """Retorna dados agregados por UF"""
    if not supabase: return []
    res = supabase.table("candidatos").select("estado, comentarios_totais_count, comentarios_odio_count").execute()
    
    stats = {}
    for c in res.data:
        uf = (c['estado'] or 'BR').upper()
        if uf not in stats: stats[uf] = {"alvos": 0, "alertas": 0}
        stats[uf]["alvos"] += 1
        stats[uf]["alertas"] += (c['comentarios_odio_count'] or 0)
    
    return stats

