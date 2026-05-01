from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from collections import Counter

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supa():
    if not SUPABASE_URL or not SUPABASE_KEY: return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def calculate_risk(item):
    """Calcula score de risco dinâmico para a UI"""
    totais = item.get('comentarios_totais_count', 0) or 0
    odio = item.get('comentarios_odio_count', 0) or 0
    
    if totais == 0: return 0, 'CONTROLADO', '#10b981'
    
    ratio = odio / totais
    score = min(100, int(ratio * 200) + min(30, odio // 5))
    
    if ratio > 0.25 or odio > 50: return score, 'CRITICO', '#ef4444'
    if ratio > 0.15 or odio > 20: return score, 'ELEVADO', '#f59e0b'
    if ratio > 0.05 or odio > 5: return score, 'MONITORANDO', '#06b6d4'
    return score, 'CONTROLADO', '#10b981'

@app.get("/api/v1/summary")
def summary():
    try:
        supa = get_supa()
        if not supa: return {"error": "DB credentials missing"}
        
        # Uso de count='exact' para evitar carregar milhares de linhas
        c_res = supa.table('candidatos').select('id', count='exact').execute()
        t_res = supa.table('comentarios').select('id', count='exact').execute()
        h_res = supa.table('comentarios').select('id', count='exact').eq('is_hate', True).execute()
        
        c = c_res.count if c_res.count is not None else 0
        t = t_res.count if t_res.count is not None else 0
        h = h_res.count if h_res.count is not None else 0
        
        res = round((t-h)/t*100, 1) if t > 0 else 100
        return {
            "total_monitorados": c, 
            "total_alertas": h, 
            "total_amostra": t, 
            "resiliencia": res,
            "trends": {"hate_trend_pct": 0, "resiliencia_trend_pct": 0}
        }
    except Exception as e: return {"error": str(e)}

@app.get("/api/v1/trends")
def trends(days: int = 30):
    try:
        supa = get_supa()
        if not supa: return []
        return supa.table('comentarios').select('autor_username, texto_bruto, categoria_ia, confianza_ia, data_coleta, candidato_id').eq('is_hate', True).order('data_coleta', desc=True).limit(50).execute().data
    except Exception as e: return {"error": str(e)}

@app.get("/api/v1/targets")
def get_targets(limit: int = 50):
    try:
        supa = get_supa()
        if not supa: return []
        data = supa.table('candidatos').select('*').order('username').limit(limit).execute().data
        
        enriched = []
        for item in data:
            score, nivel, color = calculate_risk(item)
            enriched.append({
                **item,
                "score_risco": score,
                "nivel_risco": nivel,
                "color": color,
                "comentarios_totales_count": item.get('comentarios_totais_count', 0)
            })
        return sorted(enriched, key=lambda x: x['score_risco'], reverse=True)
    except Exception as e: return {"error": str(e)}

@app.get("/api/v1/alerts/active")
def get_active_alerts(limit: int = 20):
    try:
        supa = get_supa()
        if not supa: return []
        return supa.table('comentarios').select('*, candidatos(username)').eq('is_hate', True).order('data_coleta', desc=True).limit(limit).execute().data
    except Exception as e: return {"error": str(e)}

@app.get("/api/v1/networks")
def get_networks():
    return []

@app.get("/api/v1/pasa/breakdown")
def pasa_breakdown():
    try:
        supa = get_supa()
        if not supa: return []
        # Busca categorias apenas dos comentários de ódio recentes para breakdown
        res = supa.table('comentarios').select('categoria_ia').eq('is_hate', True).limit(1000).execute()
        counts = Counter([i['categoria_ia'] for i in res.data if i.get('categoria_ia')])
        
        PASA_CONFIG = {
            "ODIO_IDENTITARIO":    {"label": "Ódio Identitário",   "color": "#ef4444", "icon": "users"},
            "VIOLENCIA_GENERO":    {"label": "Violência de Gênero","color": "#ec4899", "icon": "shield-alert"},
            "AMEACA":              {"label": "Ameaça",             "color": "#f97316", "icon": "alert-octagon"},
            "INSULTO_AD_HOMINEM":  {"label": "Insulto Ad Hominem", "color": "#f59e0b", "icon": "swords"},
            "ATAQUE_INSTITUCIONAL":{"label": "Ataque Institucional","color": "#8b5cf6", "icon": "landmark"},
            "RIGOR_CRIMINAL":      {"label": "Rigor Criminal",     "color": "#06b6d4", "icon": "scale"},
        }
        
        total_total = sum(counts.values())
        return [{
            "categoria_ia": cat,
            "total": val,
            "percentual": round(val/total_total*100, 1) if total_total > 0 else 0,
            "label": PASA_CONFIG.get(cat, {}).get("label", cat),
            "color": PASA_CONFIG.get(cat, {}).get("color", "#64748b"),
            "icon": PASA_CONFIG.get(cat, {}).get("icon", "help-circle")
        } for cat, val in counts.items()]
    except Exception as e: return {"error": str(e)}

@app.get("/api/v1/geo/uf")
def geo_uf():
    try:
        supa = get_supa()
        if not supa: return []
        # Busca estados dos candidatos
        cands = supa.table('candidatos').select('username, estado').execute().data
        uf_map = {c['username']: (c.get('estado') or 'N/A') for c in cands}
        
        # Busca comentários de ódio (limite para evitar timeout)
        coms = supa.table('comentarios').select('candidato_id').eq('is_hate', True).limit(2000).execute().data
        counts = Counter([uf_map.get(c['candidato_id'], 'N/A') for c in coms])
        
        RISK_COLORS = {
            "CRITICO": "#ef4444",
            "ELEVADO": "#f59e0b",
            "MONITORANDO": "#06b6d4",
            "CONTROLADO": "#10b981",
        }
        
        return [{
            "uf": uf,
            "total_hate": val,
            "total_alvos": len([u for u, s in uf_map.items() if s == uf]),
            "nivel_risco": "ELEVADO" if val > 10 else "MONITORANDO",
            "color": RISK_COLORS.get("ELEVADO" if val > 10 else "MONITORANDO")
        } for uf, val in counts.items()]
    except Exception as e: return {"error": str(e)}

@app.get("/api/health")
def health():
    return {"status": "operational", "db": get_supa() is not None}
