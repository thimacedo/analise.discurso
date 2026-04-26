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
import pyotp
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

STOPWORDS = {"a", "o", "que", "e", "do", "da", "em", "um", "para", "com", "não", "uma", "os", "as", "no", "na", "por", "mais", "mas", "ao", "se", "como", "esta", "está"}

def extract_idiolect(texts: List[str]) -> List[str]:
    words = []
    for text in texts:
        tokens = re.findall(r'\b\w{4,}\b', text.lower())
        words.extend([t for t in tokens if t not in STOPWORDS])
    return [word for word, count in Counter(words).most_common(5)]

# --- ROTAS DE API ---

@app.get("/api/v1/stats/neighborhood")
async def get_attack_neighborhood():
    """Identifica autores que atacam múltiplos alvos (Redes Coordenadas)"""
    url = f"{SUPABASE_URL}/rest/v1/comentarios?select=autor,candidato_id&is_hate=eq.true&limit=1000"
    async with httpx.AsyncClient() as client:
        res = await client.get(url, headers=get_supabase_headers())
        if res.status_code != 200: return []
        data = res.json()
        
        # Mapear Autor -> Lista de Alvos
        author_map = {}
        for item in data:
            autor = item['autor']
            alvo = item['candidato_id']
            if autor == 'anonimo' or not autor: continue
            if autor not in author_map: author_map[autor] = set()
            author_map[autor].add(alvo)
        
        # Filtrar apenas quem ataca > 1 alvo
        networks = []
        for author, targets in author_map.items():
            if len(targets) > 1:
                networks.append({"autor": author, "alvos": list(targets), "intensidade": len(targets)})
        
        return sorted(networks, key=lambda x: x['intensidade'], reverse=True)[:10]

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    url_c = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,estado,comentarios_totais_count,comentarios_odio_count&status_monitoramento=ilike.Ativo&order=comentarios_totais_count.desc&limit=24"
    async with httpx.AsyncClient() as client:
        res_c = await client.get(url_c, headers=get_supabase_headers())
        if res_c.status_code != 200: return []
        candidatos = res_c.json()

        two_days_ago = (datetime.now() - timedelta(days=2)).isoformat()
        url_h = f"{SUPABASE_URL}/rest/v1/comentarios?select=candidato_id,texto_bruto,data_coleta&is_hate=eq.true&data_coleta=gt.{two_days_ago}"
        res_h = await client.get(url_h, headers=get_supabase_headers())
        hate_data = res_h.json() if res_h.status_code == 200 else []

        processed = []
        for c in candidatos:
            un = c['username']
            total = c.get('comentarios_totais_count') or 0
            odio = c.get('comentarios_odio_count') or 0
            blindagem = 100.0 - ((odio / total * 100) if total > 0 else 0)
            target_hate = [h for h in hate_data if h['candidato_id'] == un]
            idioleto = extract_idiolect([h['texto_bruto'] for h in target_hate if h.get('texto_bruto')])
            
            timeline = [0] * 8
            now = datetime.now()
            for h in target_hate:
                try:
                    dt = datetime.fromisoformat(h['data_coleta'].replace('Z', '+00:00'))
                    diff = now - dt.replace(tzinfo=None)
                    idx = 7 - int(diff.total_seconds() // (6 * 3600))
                    if 0 <= idx < 8: timeline[idx] += 1
                except: continue

            processed.append({
                "username": un, "estado": c['estado'], "share_blindagem": round(blindagem, 2),
                "idioleto": idioleto if idioleto else ["Estável"], "timeline": timeline
            })
        return processed

@app.get("/")
async def home_page():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), media_type="text/html; charset=utf-8")

@app.get("/api/v1/status")
async def status():
    return {"status": "online", "version": "15.6.9"}
