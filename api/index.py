import os
import asyncio
import httpx
import json
import io
import base64
import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

if os.path.exists("src"): app.mount("/src", StaticFiles(directory="src"), name="src")
if os.path.exists("docs"): app.mount("/docs", StaticFiles(directory="docs"), name="docs")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# --- ROTAS DE API ---

@app.get("/api/v1/admin/comments/review")
async def list_comments_for_review(limit: int = 50, offset: int = 0, is_hate: Optional[bool] = None):
    url = f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.true&order=data_coleta.desc&limit={limit}&offset={offset}"
    if is_hate is not None:
        url += f"&is_hate=eq.{str(is_hate).lower()}"
    
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=get_supabase_headers())
        return res.json() if res.status_code == 200 else []

@app.patch("/api/v1/admin/comments/{comment_id}")
async def update_comment_classification(comment_id: int, data: dict = Body(...)):
    url = f"{SUPABASE_URL}/rest/v1/comentarios?id=eq.{comment_id}"
    async with httpx.AsyncClient() as client:
        res = await client.patch(url, headers=get_supabase_headers(), json=data)
        if res.status_code in [200, 204]:
            return {"status": "success"}
        raise HTTPException(status_code=res.status_code, detail=res.text)

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    try:
        url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,estado,comentarios_totais_count,comentarios_odio_count&status_monitoramento=ilike.Ativo&order=comentarios_totais_count.desc&limit=10"
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.get(url, headers=get_supabase_headers())
            if res.status_code != 200: return []
            data = res.json()
            processed = []
            for c in data:
                total = c.get('comentarios_totais_count') or 0
                odio = c.get('comentarios_odio_count') or 0
                share_blindagem = 100 - ((odio / total * 100) if total > 0 else 0)
                processed.append({
                    "username": c['username'], "estado": c['estado'], "share_blindagem": round(share_blindagem, 2)
                })
            return processed
    except: return []

@app.get("/docs/analise-violencia", response_class=HTMLResponse)
@app.get("/docs/analise-violencia.html", response_class=HTMLResponse)
async def analise_page():
    with open("docs/analise-violencia.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="text/html; charset=utf-8")

@app.get("/docs/metodologia", response_class=HTMLResponse)
@app.get("/docs/metodologia.html", response_class=HTMLResponse)
async def metodologia_page():
    with open("docs/metodologia.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="text/html; charset=utf-8")

@app.get("/", response_class=HTMLResponse)
async def home_page():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="text/html; charset=utf-8")

@app.get("/api/v1/status")
async def status():
    return {"status": "online", "version": "15.7.6"}
