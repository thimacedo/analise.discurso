import os
import httpx
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# --- API ---
@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    try:
        url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,estado,comentarios_totais_count,comentarios_odio_count&comentarios_totais_count=gt.0&order=comentarios_totais_count.desc&limit=12"
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(url, headers=get_supabase_headers())
            if res.status_code != 200: return []
            data = res.json()
            return [{"username": c['username'], "estado": c['estado'], "share_blindagem": round(100 - ((c.get('comentarios_odio_count', 0) / c.get('comentarios_totais_count', 1)) * 100), 2)} for c in data]
    except: return []

@app.get("/api/v1/live-intelligence")
async def get_live_intelligence():
    try:
        if os.path.exists("data/pasa_live_logs.json"):
            with open("data/pasa_live_logs.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    except: return []

@app.get("/api/v1/status")
async def status():
    return {"status": "online", "version": "15.8.8"}

# --- ROTEADOR UNIVERSAL (FRONTEND) ---
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, full_path: str):
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    
    # 1. Mapear rotas para arquivos físicos
    route_map = {
        "": "index.html",
        "admin": "addalvo.html",
        "docs/analise-violencia": "docs/analise-violencia.html",
        "docs/metodologia": "docs/metodologia.html"
    }
    
    # Remover slash final se houver
    clean_path = full_path.rstrip("/")
    target_file = route_map.get(clean_path)
    
    if target_file:
        file_path = os.path.join(base_dir, target_file)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    
    # 2. Se for um arquivo estático (JS/CSS)
    file_path = os.path.join(base_dir, full_path)
    if os.path.exists(file_path) and not os.path.isdir(file_path):
        # Para estáticos, o Vercel deveria cuidar, mas como fallback:
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())

    return HTMLResponse(content="<h1>404 - Rota nao encontrada no Sentinela</h1>", status_code=404)
