from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
supa = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@app.get("/api/v1/summary")
def summary():
    total_c = len(supa.table('candidatos').select('id').execute().data)
    total_com = len(supa.table('comentarios').select('id').execute().data)
    total_hate = len(supa.table('comentarios').select('id').eq('is_hate', True).execute().data)
    res = round((total_com - total_hate)/total_com*100, 1) if total_com > 0 else 100
    return {"monitorados": total_c, "odio": total_hate, "total": total_com, "resiliencia": res}

@app.get("/api/v1/trends")
def trends(days: int = 30):
    return supa.table('comentarios').select('autor_username, texto_bruto, categoria_ia, confianza_ia, data_coleta, candidato_id').eq('is_hate', True).order('data_coleta', desc=True).limit(50).execute().data

@app.get("/api/v1/pasa/breakdown")
def pasa_breakdown():
    res = supa.table('comentarios').select('categoria_ia').eq('is_hate', True).execute()
    return dict(Counter([i['categoria_ia'] for i in res.data if i.get('categoria_ia')]))

@app.get("/api/v1/geo/uf")
def geo_uf():
    # Nota: a coluna no banco pode ser 'estado', ajustando para compatibilidade
    cands = supa.table('candidatos').select('username, estado').execute().data
    uf_map = {c['username']: c.get('estado', 'N/A') for c in cands}
    coms = supa.table('comentarios').select('candidato_id').eq('is_hate', True).execute().data
    return dict(Counter([uf_map.get(c['candidato_id'], 'N/A') for c in coms]))
