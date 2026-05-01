from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

@app.get("/api/v1/summary")
def summary():
    try:
        if not SUPABASE_URL or not SUPABASE_KEY: return {"error": "ENV missing"}
        supa = create_client(SUPABASE_URL, SUPABASE_KEY)
        c = len(supa.table('candidatos').select('id').execute().data)
        t = len(supa.table('comentarios').select('id').execute().data)
        h = len(supa.table('comentarios').select('id').eq('is_hate', True).execute().data)
        return {"monitorados": c, "odio": h, "total": t, "resiliencia": round((t-h)/t*100, 1) if t > 0 else 100}
    except Exception as e: return {"error": str(e)}

@app.get("/api/v1/trends")
def trends(days: int = 30):
    try:
        if not SUPABASE_URL or not SUPABASE_KEY: return {"error": "ENV missing"}
        supa = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supa.table('comentarios').select('autor_username, texto_bruto, categoria_ia, confianza_ia, data_coleta, candidato_id').eq('is_hate', True).order('data_coleta', desc=True).limit(50).execute().data
    except Exception as e: return {"error": str(e)}

@app.get("/api/v1/pasa/breakdown")
def pasa_breakdown():
    try:
        if not SUPABASE_URL or not SUPABASE_KEY: return {"error": "ENV missing"}
        supa = create_client(SUPABASE_URL, SUPABASE_KEY)
        res = supa.table('comentarios').select('categoria_ia').eq('is_hate', True).execute()
        from collections import Counter
        return dict(Counter([i['categoria_ia'] for i in res.data if i.get('categoria_ia')]))
    except Exception as e: return {"error": str(e)}

@app.get("/api/v1/geo/uf")
def geo_uf():
    try:
        if not SUPABASE_URL or not SUPABASE_KEY: return {"error": "ENV missing"}
        supa = create_client(SUPABASE_URL, SUPABASE_KEY)
        cands = supa.table('candidatos').select('username, uf').execute().data
        uf_map = {c['username']: c.get('uf', 'N/A') for c in cands}
        coms = supa.table('comentarios').select('candidato_id').eq('is_hate', True).execute().data
        from collections import Counter
        return dict(Counter([uf_map.get(c['candidato_id'], 'N/A') for c in coms]))
    except Exception as e: return {"error": str(e)}