import os
import httpx
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

@app.get("/api/v1/status")
async def status():
    # Teste de conectividade com Supabase
    db_status = "error"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(f"{SUPABASE_URL}/rest/v1/candidatos?select=id&limit=1", headers=get_supabase_headers())
            if res.status_code == 200: db_status = "connected"
    except: pass
    
    return {
        "status": "online",
        "version": "15.11.8",
        "database": db_status
    }

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    try:
        # Busca direta para popular o gráfico
        url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,estado,comentarios_totais_count,comentarios_odio_count&comentarios_totais_count=gt.0&order=comentarios_totais_count.desc&limit=10"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=get_supabase_headers())
            if res.status_code != 200: return []
            
            data = res.json()
            processed = []
            for c in data:
                total = c.get('comentarios_totais_count') or 1
                odio = c.get('comentarios_odio_count') or 0
                processed.append({
                    "username": c['username'],
                    "estado": c['estado'],
                    "share_blindagem": round(100 - ((odio / total) * 100), 2)
                })
            return processed
    except Exception as e:
        print(f"API Error: {e}")
        return []

# Fallback para rotas de debug
@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
