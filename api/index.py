import os
import httpx
import json
from fastapi import FastAPI
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
    return {"status": "online", "version": "15.9.3"}

# --- ROTAS EXPLÍCITAS (FIM DO 404) ---

def serve_html(filename):
    # Procura no root do projeto
    path = os.path.join(os.path.dirname(__file__), "..", filename)
    if not os.path.exists(path):
        # Fallback para o mesmo diretório
        path = os.path.join(os.path.dirname(__file__), filename)
    
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/", response_class=HTMLResponse)
async def home(): return serve_html("index.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin(): return serve_html("addalvo.html")

@app.get("/analise-extremismo", response_class=HTMLResponse)
async def analise(): return serve_html("analise-extremismo.html")

@app.get("/metodologia", response_class=HTMLResponse)
async def metodologia(): return serve_html("metodologia.html")
