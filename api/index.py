from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

app = FastAPI(title="Sentinela API", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Configuração Supabase com Fallback para Debug
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ AVISO: SUPABASE_URL ou SUPABASE_KEY não configurados!")

supa = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Router para versionamento v1
router = APIRouter(prefix="/api/v1")

@router.get("/summary")
def summary():
    if not supa: return {"error": "DB disconnected"}
    try:
        total_c = len(supa.table('candidatos').select('id').execute().data)
        total_com = len(supa.table('comentarios').select('id').execute().data)
        total_hate = len(supa.table('comentarios').select('id').eq('is_hate', True).execute().data)
        res = round((total_com - total_hate)/total_com*100, 1) if total_com > 0 else 100
        return {"monitorados": total_c, "odio": total_hate, "total": total_com, "resiliencia": res}
    except Exception as e:
        return {"error": str(e)}

@router.get("/trends")
def trends(days: int = 30):
    if not supa: return []
    try:
        return supa.table('comentarios').select('autor_username, texto_bruto, categoria_ia, confianza_ia, data_coleta, candidato_id').eq('is_hate', True).order('data_coleta', desc=True).limit(50).execute().data
    except Exception:
        return []

@router.get("/pasa/breakdown")
def pasa_breakdown():
    if not supa: return {}
    try:
        res = supa.table('comentarios').select('categoria_ia').eq('is_hate', True).execute()
        return dict(Counter([i['categoria_ia'] for i in res.data if i.get('categoria_ia')]))
    except Exception:
        return {}

@router.get("/geo/uf")
def geo_uf():
    if not supa: return {}
    try:
        cands = supa.table('candidatos').select('username, estado').execute().data
        uf_map = {c['username']: c.get('estado', 'N/A') for c in cands}
        coms = supa.table('comentarios').select('candidato_id').eq('is_hate', True).execute().data
        return dict(Counter([uf_map.get(c['candidato_id'], 'N/A') for c in coms]))
    except Exception:
        return {}

# Inclusão do router no app principal
app.include_router(router)

# Health Check na raiz da API
@app.get("/api/health")
def health():
    return {"status": "operational", "db": supa is not None}

