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
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

@app.get("/api/v1/status")
async def status():
    return {"status": "online", "version": "15.16.2", "protocol": "PASA Mapping Active"}

@app.get("/api/v1/stats/top-alvos")
async def get_top_alvos():
    try:
        url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,estado,comentarios_totais_count,comentarios_odio_count&comentarios_totais_count=gt.0&order=comentarios_totais_count.desc&limit=10"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=get_supabase_headers())
            if res.status_code != 200: return []
            
            data = res.json()
            processed = []
            for c in data:
                total = c.get('comentarios_totais_count') or 1
                odio = c.get('comentarios_odio_count') or 0
                processed.append({
                    "username": c['username'],
                    "estado": c['estado'],
                    "share_blindagem": round(100 - ((odio / total) * 100), 2),
                    "totais": total,
                    "alertas": odio
                })
            return processed
    except:
        return []

@app.get("/api/v1/live-intelligence")
async def get_live_intelligence():
    try:
        url = f"{SUPABASE_URL}/rest/v1/comentarios?select=texto_bruto,candidato_id,is_hate&order=created_at.desc&limit=5"
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.get(url, headers=get_supabase_headers())
            if res.status_code != 200: return []
            return [{"alvo": c['candidato_id'], "texto": c['texto_bruto'], "is_hate": c['is_hate']} for c in res.json()]
    except:
        return []
