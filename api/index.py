import os
import httpx
import json
import re
from collections import Counter
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
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

# --- ROTAS DE API ---

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    try:
        # REMOVIDO FILTRO DE STATUS: Foco total em trazer quem tem dados
        url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,estado,comentarios_totais_count,comentarios_odio_count&comentarios_totais_count=gt.0&order=comentarios_totais_count.desc&limit=12"
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.get(url, headers=get_supabase_headers())
            if res.status_code != 200: 
                print(f"🔴 Erro Supabase: {res.status_code} - {res.text}")
                return []
                
            data = res.json()
            if not isinstance(data, list): return []

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
    except Exception as e:
        print(f"🔴 Falha Crítica API: {e}")
        return []

@app.get("/api/v1/live-intelligence")
async def get_live_intelligence():
    try:
        # Tenta ler do diretório de dados persistentes do Vercel
        path = "data/pasa_live_logs.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except: return []

@app.get("/api/v1/status")
async def status():
    return {"status": "online", "version": "15.8.4", "engine": "Sentinela Core"}

@app.get("/api/{path_name:path}")
async def catch_all_api(path_name: str):
    return JSONResponse({"error": "Endpoint nao encontrado", "path": path_name}, status_code=404)
