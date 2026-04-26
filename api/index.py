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

@app.get("/api/v1/status")
async def status():
    return {"status": "online", "version": "15.9.6"}

# --- ROTEAMENTO MANUAL DE FRONTEND ---

def serve_html(filename):
    # Procura no sandbox do Vercel
    base_dir = os.path.dirname(__file__)
    possible_paths = [
        os.path.join(base_dir, "..", filename),
        os.path.join(base_dir, filename),
        os.path.join("/var/task", filename)
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    return HTMLResponse(content=f"<h1>404</h1><p>Arquivo {filename} nao localizado.</p>", status_code=404)

@app.get("/", response_class=HTMLResponse)
async def root(): return serve_html("index.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin(): return serve_html("addalvo.html")

@app.get("/analise", response_class=HTMLResponse)
async def analise(): return serve_html("analise.html")

@app.get("/metodo", response_class=HTMLResponse)
async def metodo(): return serve_html("metodo.html")
