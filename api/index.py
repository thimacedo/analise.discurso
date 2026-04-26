import os
import httpx
from fastapi import FastAPI
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
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

@app.get("/api/v1/status")
async def status():
    return {"status": "online", "version": "15.11.5", "mode": "Pure API"}

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    try:
        url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,estado,comentarios_totais_count,comentarios_odio_count&comentarios_totais_count=gt.0&order=comentarios_totais_count.desc&limit=12"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=get_supabase_headers())
            return res.json() if res.status_code == 200 else []
    except: return []

@app.get("/api/v1/live-intelligence")
async def get_live_intelligence():
    # Em produção, o arquivo de log deve ser lido de um local persistente ou DB.
    # Por enquanto, retornamos vazio para evitar erros de leitura.
    return []
