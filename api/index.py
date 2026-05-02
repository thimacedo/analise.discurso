from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from collections import Counter
import traceback
import logging
from datetime import datetime

# Configuração de logs
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
        score = min(100, int(ratio * 150) + min(50, odio))
        if score > 80 or ratio > 0.25: return score, 'CRITICO', '#ef4444'
        if score > 50 or ratio > 0.15: return score, 'ELEVADO', '#f59e0b'
        if score > 20 or ratio > 0.05: return score, 'MONITORANDO', '#06b6d4'
        return score, 'CONTROLADO', '#10b981'
    except:
        return 0, 'N/A', '#64748b'

@app.get("/api/v1/summary")
def summary():
    try:
        supa = get_supa()
        if not supa: return {"error": "DB credentials missing"}
        c_res = supa.table('candidatos').select('id', count='exact').limit(0).execute()
        t_res = supa.table('comentarios').select('id', count='exact').execute()
        h_res = supa.table('comentarios').select('id', count='exact').eq('is_hate', True).execute()
        c = c_res.count if c_res and c_res.count is not None else 0
        t = t_res.count if t_res and t_res.count is not None else 0
        h = h_res.count if h_res and h_res.count is not None else 0
        res = round((t-h)/t*100, 1) if t > 0 else 100
        return {"total_monitorados": c, "total_alertas": h, "total_amostra": t, "resiliencia": res, "trends": {"hate_trend_pct": 0, "resiliencia_trend_pct": 0}}
    except Exception as e: return {"error": str(e), "trace": traceback.format_exc()}

@app.get("/api/v1/trends")
def trends(days: int = 30):
    try:
        supa = get_supa()
        if not supa: return []
        res = supa.table('comentarios').select('autor_username, texto_bruto, categoria_ia, confianza_ia, data_coleta, candidato_id, plataforma').eq('is_hate', True).order('data_coleta', desc=True).limit(2000).execute()
        return res.data if res and res.data else []
    except Exception as e: return []

@app.get("/api/v1/targets")
def get_targets(limit: int = 50):
    try:
        supa = get_supa()
        if not supa: return []
        h_res = supa.table('comentarios').select('candidato_id, categoria_ia').eq('is_hate', True).limit(5000).execute()
        h_data = h_res.data if h_res and h_res.data else []
        real_hate_counts = Counter([h['candidato_id'] for h in h_data if h.get('candidato_id')])
        breakdowns = {}
        for h in h_data:
            cid = h['candidato_id']
            cat = h['categoria_ia'] or 'OUTROS'
            if cid not in breakdowns: breakdowns[cid] = Counter()
            breakdowns[cid][cat] += 1
        res = supa.table('candidatos').select('*').execute()
        data = res.data if res and res.data else []
        enriched = []
        for item in data:
            cid = item.get('username')
            item['comentarios_odio_count'] = real_hate_counts.get(cid, 0)
            if item.get('comentarios_totais_count', 0) < item['comentarios_odio_count']:
                item['comentarios_totais_count'] = item['comentarios_odio_count'] + 10
            score, nivel, color = calculate_risk(item)
            enriched.append({**item, "score_risco": score, "nivel_risco": nivel, "color": color, "comentarios_totales_count": item.get('comentarios_totais_count', 0), "breakdown": dict(breakdowns.get(cid, {}))})
        return sorted(enriched, key=lambda x: x.get('comentarios_odio_count', 0), reverse=True)[:limit]
    except Exception as e: return [{"error": str(e)}]

@app.get("/api/v1/alerts/active")
def get_active_alerts(limit: int = 20):
    try:
        supa = get_supa()
        if not supa: return []
        res = supa.table('comentarios').select('*, candidatos(username)').eq('is_hate', True).order('data_coleta', desc=True).limit(2000).execute()
        return res.data if res and res.data else []
    except Exception: return []

@app.post("/api/v1/alerts/false-positive")
def mark_false_positive(payload: dict = Body(...)):
    """Marca um comentário como falso positivo para treinar a IA e limpar o dashboard"""
    try:
        supa = get_supa()
        comment_id = payload.get("id")
        if not supa or not comment_id: return {"status": "error", "message": "Invalid ID"}
        
        # 1. Busca conteúdo para log de aprendizado (Sinalização para a IA)
        comment = supa.table('comentarios').select('*').eq('id', comment_id).single().execute().data
        
        # 2. Atualiza no banco: is_hate=False e flag de falso positivo
        supa.table('comentarios').update({
            "is_hate": False, 
            "processado_ia": True, 
            "categoria_ia": "FALSO_POSITIVO_MANUAL",
            "confianza_ia": 1.0
        }).eq('id', comment_id).execute()
        
        logger.info(f"Falso Positivo marcado: {comment_id}. Feedback IA registrado.")
        return {"status": "success", "id": comment_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/networks")
def get_networks(days: int = 7):
    try:
        supa = get_supa()
        if not supa: return {"nodes": [], "links": []}
        res = supa.table('comentarios').select('autor_username, candidato_id, data_publicacao, plataforma').eq('is_hate', True).limit(5000).execute()
        data = res.data if res and res.data else []
        nodes = {}
        links = []
        author_targets = {} # Rastreia quantos alvos diferentes cada autor atacou
        for item in data:
            author = item.get('autor_username')
            target = item.get('candidato_id')
            if not author or not target: continue
            if author not in author_targets: author_targets[author] = set()
            author_targets[author].add(target)
            if author not in nodes: nodes[author] = {"id": author, "type": "author", "val": 1}
            else: nodes[author]["val"] += 1
            if target not in nodes: nodes[target] = {"id": target, "type": "target", "val": 1}
            else: nodes[target]["val"] += 1
            links.append({"source": author, "target": target, "weight": 1})
            
        # Filtro para Matriz: Apenas agressores com múltiplos alvos
        multi_target_authors = [a for a, t in author_targets.items() if len(t) > 1]
        
        return {"nodes": list(nodes.values()), "links": links[:1000], "multi_target_authors": multi_target_authors}
    except Exception as e: return {"error": str(e)}

@app.get("/api/v1/pasa/breakdown")
def pasa_breakdown():
    try:
        supa = get_supa()
        if not supa: return []
        res = supa.table('comentarios').select('categoria_ia').eq('is_hate', True).limit(1000).execute()
        data = res.data if res and res.data else []
        counts = Counter([i.get('categoria_ia') for i in data if i.get('categoria_ia')])
        PASA_CONFIG = {"ODIO_IDENTITARIO": {"label": "Ódio Identitário", "color": "#ef4444", "icon": "users"}, "VIOLENCIA_GENERO": {"label": "Violência de Gênero","color": "#ec4899", "icon": "shield-alert"}, "AMEACA": {"label": "Ameaça", "color": "#f97316", "icon": "alert-octagon"}, "INSULTO_AD_HOMINEM": {"label": "Insulto Ad Hominem", "color": "#f59e0b", "icon": "swords"}, "ATAQUE_INSTITUCIONAL":{"label": "Ataque Institucional","color": "#8b5cf6", "icon": "landmark"}, "RIGOR_CRIMINAL": {"label": "Rigor Criminal", "color": "#06b6d4", "icon": "scale"}}
        total_total = sum(counts.values())
        return [{"categoria_ia": cat, "total": val, "percentual": round(val/total_total*100, 1) if total_total > 0 else 0, "label": PASA_CONFIG.get(cat, {}).get("label", cat), "color": PASA_CONFIG.get(cat, {}).get("color", "#64748b"), "icon": PASA_CONFIG.get(cat, {}).get("icon", "help-circle")} for cat, val in counts.items()]
    except Exception as e: return []

@app.get("/api/v1/geo/uf")
def geo_uf():
    try:
        supa = get_supa()
        if not supa: return []
        cands_res = supa.table('candidatos').select('username, estado').execute()
        cands = cands_res.data if cands_res and cands_res.data else []
        uf_map = {c.get('username'): (c.get('estado') or 'N/A') for c in cands if c.get('username')}
        coms_res = supa.table('comentarios').select('candidato_id').eq('is_hate', True).limit(2000).execute()
        coms = coms_res.data if coms_res and coms_res.data else []
        counts = Counter([uf_map.get(c['candidato_id'], 'N/A') for c in coms if c.get('candidato_id')])
        RISK_COLORS = {"CRITICO": "#ef4444", "ELEVADO": "#f59e0b", "MONITORANDO": "#06b6d4", "CONTROLADO": "#10b981"}
        return [{"uf": uf, "total_hate": val, "total_alvos": len([u for u, s in uf_map.items() if s == uf]), "nivel_risco": "ELEVADO" if val > 10 else "MONITORANDO", "color": RISK_COLORS.get("ELEVADO" if val > 10 else "MONITORANDO")} for uf, val in counts.items()]
    except Exception as e: return []

from pydantic import BaseModel
from typing import Optional, List

class PushTokenRegistration(BaseModel):
    user_id: str
    token: str
    platform: Optional[str] = "web"
    device_id: Optional[str] = None

@app.post("/api/v1/auth/register-push-token")
def register_push_token(payload: PushTokenRegistration):
    """Registra um token FCM para um usuário no Supabase."""
    try:
        supa = get_supa()
        if not supa: return {"status": "error", "message": "DB credentials missing"}
        
        # Upsert do token para evitar duplicidade
        data = {
            "user_id": payload.user_id,
            "token": payload.token,
            "platform": payload.platform,
            "device_id": payload.device_id,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        res = supa.table('user_push_tokens').upsert(
            data, 
            on_conflict="user_id,token"
        ).execute()
        
        return {"status": "success", "message": "Token registered"}
    except Exception as e:
        logger.error(f"Erro ao registrar token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/config/firebase")
def get_firebase_config():
    """Retorna as chaves públicas do Firebase para o frontend."""
    return {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "vapidKey": os.getenv("FIREBASE_VAPID_KEY")
    }

@app.get("/api/health")
def health():
    return {"status": "operational", "db": get_supa() is not None}
