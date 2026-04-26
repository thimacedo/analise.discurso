import os
import httpx
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    try:
        url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,estado,comentarios_totais_count,comentarios_odio_count&comentarios_totais_count=gt.0&order=comentarios_totais_count.desc&limit=12"
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.get(url, headers=get_supabase_headers())
            return [{"username": c['username'], "estado": c['estado'], "share_blindagem": round(100 - ((c.get('comentarios_odio_count', 0) / c.get('comentarios_totais_count', 1)) * 100), 2)} for c in res.json()] if res.status_code == 200 else []
    except: return []

@app.get("/api/v1/status")
async def status(): return {"status": "online", "version": "15.10.2"}

# --- MOTOR DE RENDERIZAÇÃO ---

def render(filename):
    # Procura na pasta api/templates/
    base = os.path.dirname(__file__)
    path = os.path.join(base, "templates", filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content=f"<h1>Erro</h1><p>Recurso {filename} nao localizado.</p>", status_code=404)

@app.get("/")
async def home(): return render("index.html")

@app.get("/admin")
async def admin(): return render("addalvo.html")

@app.get("/analise")
async def analise(): return render("analise.html")

@app.get("/metodo")
async def metodo(): return render("metodo.html")

# Servir estáticos de forma explícita se o Vercel falhar
@app.get("/src/{path:path}")
async def serve_src(path: str):
    base = os.path.join(os.path.dirname(__file__), "src", path)
    if os.path.exists(base):
        with open(base, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return JSONResponse({"error": "Static not found"}, status_code=404)
