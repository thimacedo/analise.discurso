import os
import httpx
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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
@app.get("/api/v1/status")
async def status():
    return {"status": "online", "version": "15.11.3", "project": "Sentinela Core Unified"}

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    try:
        url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,estado,comentarios_totais_count,comentarios_odio_count&comentarios_totais_count=gt.0&order=comentarios_totais_count.desc&limit=12"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=get_supabase_headers())
            return res.json() if res.status_code == 200 else []
    except: return []

# --- ROTEAMENTO BLINDADO (ROOT-SANDBOX) ---
def serve(filename):
    base_dir = os.path.dirname(__file__)
    # Vercel Task Root é um nível acima da pasta api/
    path = os.path.abspath(os.path.join(base_dir, "..", filename))
    
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content=f"<h1>Erro</h1><p>Arquivo {filename} não localizado no servidor.</p>", status_code=404)

@app.get("/", response_class=HTMLResponse)
async def home(): return serve("index.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin(): return serve("addalvo.html")

@app.get("/analise", response_class=HTMLResponse)
async def analise(): return serve("analise.html")

@app.get("/metodo", response_class=HTMLResponse)
async def metodo(): return serve("metodo.html")
