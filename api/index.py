from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from collections import Counter
import traceback
import logging

# Configuração de logs conforme Passo 3 do plano de debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("sentinela-api")

load_dotenv()
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supa():
    try:
        if not SUPABASE_URL or not SUPABASE_KEY: 
            logger.error("Credenciais do Supabase ausentes no ambiente.")
            return None
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Erro ao conectar com Supabase: {e}")
        return None

def calculate_risk(item):
    """Calcula score de risco dinâmico para a UI"""
    try:
        totais = item.get('comentarios_totais_count', 0) or 0
        odio = item.get('comentarios_odio_count', 0) or 0
        
        if totais == 0: return 0, 'CONTROLADO', '#10b981'
        
        ratio = odio / totais
        score = min(100, int(ratio * 200) + min(30, odio // 5))
        
        if ratio > 0.25 or odio > 50: return score, 'CRITICO', '#ef4444'
        if ratio > 0.15 or odio > 20: return score, 'ELEVADO', '#f59e0b'
        if ratio > 0.05 or odio > 5: return score, 'MONITORANDO', '#06b6d4'
        return score, 'CONTROLADO', '#10b981'
    except:
        return 0, 'N/A', '#64748b'

@app.get("/api/v1/summary")
def summary():
    logger.debug("Iniciando requisição /api/v1/summary")
    try:
        supa = get_supa()
        if not supa: return {"error": "DB credentials missing"}
        
        # Otimizado: count='exact' com limit(0) para não baixar dados
        c_res = supa.table('candidatos').select('*', count='exact').limit(0).execute()
        t_res = supa.table('comentarios').select('*', count='exact').limit(0).execute()
        h_res = supa.table('comentarios').select('*', count='exact').eq('is_hate', True).limit(0).execute()
        
        c = c_res.count if c_res and c_res.count is not None else 0
        t = t_res.count if t_res and t_res.count is not None else 0
        h = h_res.count if h_res and h_res.count is not None else 0
        
        res = round((t-h)/t*100, 1) if t > 0 else 100
        logger.info(f"Summary gerado: {c} monitorados, {h} alertas.")
        return {
            "total_monitorados": c, 
            "total_alertas": h, 
            "total_amostra": t, 
            "resiliencia": res,
            "trends": {"hate_trend_pct": 0, "resiliencia_trend_pct": 0}
        }
    except Exception as e: 
        logger.error(f"Erro em /summary: {e}")
        return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/api/v1/trends")
def trends(days: int = 30):
    logger.debug(f"Iniciando requisição /api/v1/trends (days={days})")
    try:
        supa = get_supa()
        if not supa: return []
        res = supa.table('comentarios').select('autor_username, texto_bruto, categoria_ia, confianza_ia, data_coleta, candidato_id').eq('is_hate', True).order('data_coleta', desc=True).limit(50).execute()
        return res.data if res and res.data else []
    except Exception as e:
        logger.error(f"Erro em /trends: {e}")
        return []

@app.get("/api/v1/targets")
def get_targets(limit: int = 50):
    logger.debug(f"Iniciando requisição /api/v1/targets (limit={limit})")
    try:
        supa = get_supa()
        if not supa: return []
        
        # 1. Busca candidatos
        res = supa.table('candidatos').select('*').order('username').limit(limit).execute()
        data = res.data if res and res.data else []
        usernames = [c['username'] for c in data if c.get('username')]
        
        # 2. Busca breakdown de categorias para esses candidatos (otimizado em um lote)
        h_res = supa.table('comentarios').select('candidato_id, categoria_ia').in_('candidato_id', usernames).eq('is_hate', True).execute()
        h_data = h_res.data if h_res and h_res.data else []
        
        # Agrupa por candidato e categoria
        breakdowns = {}
        for h in h_data:
            cid = h['candidato_id']
            cat = h['categoria_ia'] or 'OUTROS'
            if cid not in breakdowns: breakdowns[cid] = Counter()
            breakdowns[cid][cat] += 1
        
        enriched = []
        for item in data:
            score, nivel, color = calculate_risk(item)
            cid = item.get('username')
            enriched.append({
                **item,
                "score_risco": score,
                "nivel_risco": nivel,
                "color": color,
                "comentarios_totales_count": item.get('comentarios_totais_count', 0),
                "breakdown": dict(breakdowns.get(cid, {}))
            })
        return sorted(enriched, key=lambda x: x.get('score_risco', 0), reverse=True)
    except Exception as e:
        logger.error(f"Erro em /targets: {e}")
        return [{"error": str(e)}]

@app.get("/api/v1/alerts/active")
def get_active_alerts(limit: int = 20):
    logger.debug(f"Iniciando requisição /api/v1/alerts/active (limit={limit})")
    try:
        supa = get_supa()
        if not supa: return []
        res = supa.table('comentarios').select('*, candidatos(username)').eq('is_hate', True).order('data_coleta', desc=True).limit(limit).execute()
        return res.data if res and res.data else []
    except Exception as e:
        logger.error(f"Erro em /alerts/active: {e}")
        return []

@app.get("/api/v1/networks")
def get_networks(days: int = 7):
    logger.debug(f"Iniciando requisição /api/v1/networks (days={days})")
    try:
        supa = get_supa()
        if not supa: return {"nodes": [], "links": []}
        
        # Get hate comments from recent days
        res = supa.table('comentarios').select('autor_username, candidato_id, data_publicacao').eq('is_hate', True).limit(1000).execute()
        data = res.data if res and res.data else []
        
        nodes = {}
        links = []
        
        # Simple graph logic: authors connected to targets
        for item in data:
            author = item.get('autor_username')
            target = item.get('candidato_id')
            if not author or not target: continue
            
            if author not in nodes: nodes[author] = {"id": author, "type": "author", "val": 1}
            else: nodes[author]["val"] += 1
            
            if target not in nodes: nodes[target] = {"id": target, "type": "target", "val": 1}
            else: nodes[target]["val"] += 1
            
            links.append({"source": author, "target": target, "weight": 1})
            
        logger.info(f"Rede gerada: {len(nodes)} nós, {len(links)} conexões.")
        return {
            "nodes": list(nodes.values()),
            "links": links[:500] # Limit for UI performance
        }
    except Exception as e:
        logger.error(f"Erro em /networks: {e}")
        return {"error": str(e)}

@app.get("/api/v1/pasa/breakdown")
def pasa_breakdown():
    logger.debug("Iniciando requisição /api/v1/pasa/breakdown")
    try:
        supa = get_supa()
        if not supa: return []
        res = supa.table('comentarios').select('categoria_ia').eq('is_hate', True).limit(1000).execute()
        data = res.data if res and res.data else []
        counts = Counter([i.get('categoria_ia') for i in data if i.get('categoria_ia')])
        
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
    except Exception as e: 
        logger.error(f"Erro em /pasa/breakdown: {e}")
        return []

@app.get("/api/v1/geo/uf")
def geo_uf():
    logger.debug("Iniciando requisição /api/v1/geo/uf")
    try:
        supa = get_supa()
        if not supa: return []
        
        cands_res = supa.table('candidatos').select('username, estado').execute()
        cands = cands_res.data if cands_res and cands_res.data else []
        uf_map = {c.get('username'): (c.get('estado') or 'N/A') for c in cands if c.get('username')}
        
        coms_res = supa.table('comentarios').select('candidato_id').eq('is_hate', True).limit(2000).execute()
        coms = coms_res.data if coms_res and coms_res.data else []
        counts = Counter([uf_map.get(c.get('candidato_id'), 'N/A') for c in coms])
        
        RISK_COLORS = {
            "CRITICO": "#ef4444",
            "ELEVADO": "#f59e0b",
            "MONITORANDO": "#06b6d4",
            "CONTROLADO": "#10b981",
        }
        
        result = [{
            "uf": uf,
            "total_hate": val,
            "total_alvos": len([u for u, s in uf_map.items() if s == uf]),
            "nivel_risco": "ELEVADO" if val > 10 else "MONITORANDO",
            "color": RISK_COLORS.get("ELEVADO" if val > 10 else "MONITORANDO")
        } for uf, val in counts.items()]
        
        logger.info(f"Geopolítica UF gerada para {len(result)} estados.")
        return result
    except Exception as e: 
        logger.error(f"Erro em /geo/uf: {e}\n{traceback.format_exc()}")
        return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/api/health")
def health():
    return {"status": "operational", "db": get_supa() is not None}
