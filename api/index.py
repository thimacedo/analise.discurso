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
from fastapi import FastAPI, Request, HTTPException
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

# --- UTILITÁRIOS ---

STOPWORDS = {"a", "o", "que", "e", "do", "da", "em", "um", "para", "com", "não", "uma", "os", "as", "no", "na", "por", "mais", "mas", "ao", "se", "como"}

def extract_idiolect(texts: List[str]) -> List[str]:
    try:
        words = []
        for text in texts:
            if not text: continue
            tokens = re.findall(r'\b\w{4,}\b', text.lower())
            words.extend([t for t in tokens if t not in STOPWORDS])
        return [word for word, count in Counter(words).most_common(5)]
    except: return ["Analizando"]

# --- ROTAS DE API ---

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
                    "username": c['username'],
                    "estado": c['estado'],
                    "share_blindagem": round(share_blindagem, 2)
                })
            return processed
    except Exception as e:
        print(f"ERROR top-alvos: {e}")
        return []

@app.get("/api/v1/stats/neighborhood")
async def get_attack_neighborhood():
    try:
        url = f"{SUPABASE_URL}/rest/v1/comentarios?select=autor,candidato_id&is_hate=eq.true&limit=500"
        async with httpx.AsyncClient(timeout=20.0) as client:
            res = await client.get(url, headers=get_supabase_headers())
            if res.status_code != 200: return []
            author_map = {}
            for item in res.json():
                a, target = item.get('autor'), item.get('candidato_id')
                if not a or a == 'anonimo': continue
                if a not in author_map: author_map[a] = set()
                author_map[a].add(target)
            return sorted([{"autor": k, "alvos": list(v), "intensidade": len(v)} for k, v in author_map.items() if len(v) > 1], key=lambda x: x['intensidade'], reverse=True)[:5]
    except Exception as e:
        print(f"ERROR neighborhood: {e}")
        return []

@app.get("/docs/analise-violencia", response_class=HTMLResponse)
@app.get("/docs/analise-violencia.html", response_class=HTMLResponse)
async def analise_page():
    try:
        with open("docs/analise-violencia.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), media_type="text/html; charset=utf-8")
    except: return HTMLResponse(content="P&aacute;gina n&atilde;o encontrada", status_code=404)

@app.get("/docs/metodologia", response_class=HTMLResponse)
@app.get("/docs/metodologia.html", response_class=HTMLResponse)
async def metodologia_page():
    try:
        with open("docs/metodologia.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), media_type="text/html; charset=utf-8")
    except: return HTMLResponse(content="P&aacute;gina n&atilde;o encontrada", status_code=404)

@app.get("/", response_class=HTMLResponse)
async def home_page():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), media_type="text/html; charset=utf-8")
    except: return HTMLResponse(content="Erro ao carregar Dashboard", status_code=500)

@app.get("/api/v1/status")
async def status():
    return {"status": "online", "version": "15.7.5"}
