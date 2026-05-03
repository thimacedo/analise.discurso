from fastapi import FastAPI, Query, HTTPException, Body, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from collections import Counter
import traceback
import logging
from datetime import datetime, timedelta
from api.stripe_service import payment_manager
import stripe

# Configuração de logs
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("sentinela-api")

load_dotenv()

# --- CONSTANTS ---
PASA_CONFIG = {
    "ODIO_IDENTITARIO": {"label": "Ódio Identitário", "color": "#ef4444", "icon": "users"},
    "VIOLENCIA_GENERO": {"label": "Violência de Gênero", "color": "#ec4899", "icon": "shield-alert"},
    "AMEACA": {"label": "Ameaça", "color": "#f97316", "icon": "alert-octagon"},
    "INSULTO_AD_HOMINEM": {"label": "Insulto Ad Hominem", "color": "#f59e0b", "icon": "swords"},
    "ATAQUE_INSTITUCIONAL": {"label": "Ataque Institucional", "color": "#8b5cf6", "icon": "landmark"},
    "RIGOR_CRIMINAL": {"label": "Rigor Criminal", "color": "#06b6d4", "icon": "scale"}
}
RISK_COLORS = {"CRITICO": "#ef4444", "ELEVADO": "#f59e0b", "MONITORANDO": "#06b6d4", "CONTROLADO": "#10b981"}

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

def get_supa() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Database credentials missing")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# --- MODELS ---
class CheckoutRequest(BaseModel):
    user_id: str
    package_slug: str
    price_id: Optional[str] = None

class DossierGenerateRequest(BaseModel):
    candidato_id: str

class PushTokenRegistration(BaseModel):
    user_id: str
    token: str
    platform: Optional[str] = "web"
    device_id: Optional[str] = None

# --- UTILS ---
def calculate_risk(item: Dict[str, Any]):
    totais = item.get('comentarios_totais_count', 0) or 0
    odio = item.get('comentarios_odio_count', 0) or 0
    if totais == 0: return 0, 'CONTROLADO', RISK_COLORS["CONTROLADO"]
    
    ratio = odio / totais
    score = min(100, int(ratio * 150) + min(50, odio))
    
    if score > 80 or ratio > 0.25: return score, 'CRITICO', RISK_COLORS["CRITICO"]
    if score > 50 or ratio > 0.15: return score, 'ELEVADO', RISK_COLORS["ELEVADO"]
    if score > 20 or ratio > 0.05: return score, 'MONITORANDO', RISK_COLORS["MONITORANDO"]
    return score, 'CONTROLADO', RISK_COLORS["CONTROLADO"]

# --- ENDPOINTS ---

@app.post("/api/v1/checkout/create-session")
def create_checkout(payload: CheckoutRequest):
    try:
        stn_map = {"stn_starter": 50, "stn_squad": 250, "stn_warroom": 2500}
        amount = stn_map.get(payload.package_slug, 50)
        return {"url": payment_manager.create_checkout_session(payload.user_id, amount)}
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/webhook/stripe")
async def stripe_webhook(request: Request, supa: Client = Depends(get_supa)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
        if event["type"] == "checkout.session.completed":
            meta = event["data"]["object"].get("metadata", {})
            user_id, amount = meta.get("user_id"), int(meta.get("stn_amount", 0))
            if user_id:
                res = supa.table('profiles').select('stn_tokens').eq('id', user_id).single().execute()
                current = res.data.get('stn_tokens', 0) if res.data else 0
                supa.table('profiles').update({"stn_tokens": current + amount}).eq('id', user_id).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/dossiers/generate")
async def generate_dossier(payload: DossierGenerateRequest, supa: Client = Depends(get_supa)):
    try:
        from processing.dossie_service import DossieService
        data = supa.table('comentarios').select('*').eq('candidato_id', payload.candidato_id).limit(500).execute().data
        if not data: raise HTTPException(status_code=404, detail="No data found")
        path = await DossieService().generate_dossie(data, f"data/reports/dossie_{payload.candidato_id}_{int(timedelta().total_seconds())}.pdf", payload.candidato_id)
        return {"status": "success", "pdf_url": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dossiers")
def list_dossiers(candidato_id: Optional[str] = None, supa: Client = Depends(get_supa)):
    query = supa.table('dossies').select('*')
    if candidato_id: query = query.eq('candidato_id', candidato_id)
    return query.order('data_geracao', desc=True).execute().data

@app.get("/api/v1/summary")
def summary(supa: Client = Depends(get_supa)):
    try:
        window = (datetime.utcnow() - timedelta(days=1)).isoformat()
        c = supa.table('comentarios').select('candidato_id', count='exact').gte('data_coleta', window).limit(0).execute().count or 0
        t = supa.table('comentarios').select('id', count='exact').gte('data_coleta', window).limit(0).execute().count or 0
        h = supa.table('comentarios').select('id', count='exact').eq('is_hate', True).gte('data_coleta', window).limit(0).execute().count or 0
        return {
            "total_monitorados": c, "total_alertas": h, "total_amostra": t, 
            "resiliencia": round((t - h) / t * 100, 1) if t > 0 else 100,
            "periodo": "24h", "trends": {"hate_trend_pct": 0, "resiliencia_trend_pct": 0}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/targets")
def get_targets(limit: int = 50, supa: Client = Depends(get_supa)):
    try:
        h_data = supa.table('comentarios').select('candidato_id, categoria_ia').eq('is_hate', True).limit(5000).execute().data or []
        counts = Counter([h['candidato_id'] for h in h_data if h.get('candidato_id')])
        breakdowns = {}
        for h in h_data:
            cid, cat = h['candidato_id'], h['categoria_ia'] or 'OUTROS'
            if cid not in breakdowns: breakdowns[cid] = Counter()
            breakdowns[cid][cat] += 1
        
        candidates = supa.table('candidatos').select('*').execute().data or []
        enriched = []
        for item in candidates:
            cid = item.get('username')
            item['comentarios_odio_count'] = counts.get(cid, 0)
            if item.get('comentarios_totais_count', 0) < item['comentarios_odio_count']:
                item['comentarios_totais_count'] = item['comentarios_odio_count'] + 10
            score, nivel, color = calculate_risk(item)
            enriched.append({**item, "score_risco": score, "nivel_risco": nivel, "color": color, "breakdown": dict(breakdowns.get(cid, {}))})
        return sorted(enriched, key=lambda x: x.get('comentarios_odio_count', 0), reverse=True)[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/alerts/active")
def get_active_alerts(supa: Client = Depends(get_supa)):
    return supa.table('comentarios').select('*, candidatos(username)').eq('is_hate', True).order('data_coleta', desc=True).limit(200).execute().data or []

@app.post("/api/v1/alerts/false-positive")
def mark_false_positive(payload: dict = Body(...), supa: Client = Depends(get_supa)):
    cid = payload.get("id")
    if not cid: raise HTTPException(status_code=400, detail="Invalid ID")
    supa.table('comentarios').update({"is_hate": False, "processado_ia": True, "categoria_ia": "FALSO_POSITIVO_MANUAL"}).eq('id', cid).execute()
    return {"status": "success", "id": cid}

@app.get("/api/v1/networks")
def get_networks(supa: Client = Depends(get_supa)):
    data = supa.table('comentarios').select('autor_username, candidato_id, categoria_ia').eq('is_hate', True).limit(5000).execute().data or []
    nodes, links, author_targets = {}, [], {}
    for item in data:
        a, t, cat = item.get('autor_username'), item.get('candidato_id'), item.get('categoria_ia', 'OUTROS')
        if not a or not t: continue
        if a not in author_targets: author_targets[a] = set()
        author_targets[a].add(t)
        for nid, ntype in [(a, "author"), (t, "target")]:
            if nid not in nodes: nodes[nid] = {"id": nid, "type": ntype, "val": 1}
            else: nodes[nid]["val"] += 1
        links.append({"source": a, "target": t, "weight": 1, "category": cat})
    return {"nodes": list(nodes.values()), "links": links[:2000], "multi_target_authors": [a for a, t in author_targets.items() if len(t) > 1]}

@app.get("/api/v1/pasa/breakdown")
def pasa_breakdown(supa: Client = Depends(get_supa)):
    data = supa.table('comentarios').select('categoria_ia').eq('is_hate', True).limit(1000).execute().data or []
    counts = Counter([i.get('categoria_ia') for i in data if i.get('categoria_ia')])
    total = sum(counts.values())
    return [{
        "categoria_ia": c, "total": v, "percentual": round(v/total*100, 1) if total > 0 else 0,
        **PASA_CONFIG.get(c, {"label": c, "color": "#64748b", "icon": "help-circle"})
    } for c, v in counts.items()]

@app.get("/api/v1/geo/uf")
def geo_uf(supa: Client = Depends(get_supa)):
    cands = supa.table('candidatos').select('username, estado').execute().data or []
    uf_map = {c.get('username'): (c.get('estado') or 'N/A') for c in cands if c.get('username')}
    coms = supa.table('comentarios').select('candidato_id').eq('is_hate', True).limit(2000).execute().data or []
    counts = Counter([uf_map.get(c['candidato_id'], 'N/A') for c in coms if c.get('candidato_id')])
    return [{"uf": u, "total_hate": v, "total_alvos": len([k for k, s in uf_map.items() if s == u]), "nivel_risco": "ELEVADO" if v > 10 else "MONITORANDO", "color": RISK_COLORS["ELEVADO"] if v > 10 else RISK_COLORS["MONITORANDO"]} for u, v in counts.items()]

@app.post("/api/v1/auth/register-push-token")
def register_push_token(payload: PushTokenRegistration, supa: Client = Depends(get_supa)):
    supa.table('user_push_tokens').upsert({**payload.dict(), "updated_at": datetime.utcnow().isoformat()}, on_conflict="user_id,token").execute()
    return {"status": "success"}

@app.get("/api/v1/config/firebase")
def get_firebase_config():
    return {k: os.getenv(f"FIREBASE_{k.upper()}") for k in ["API_KEY", "AUTH_DOMAIN", "PROJECT_ID", "STORAGE_BUCKET", "MESSAGING_SENDER_ID", "APP_ID", "VAPID_KEY"]}

@app.get("/api/v1/analytics/temporal-series")
def get_temporal_series(supa: Client = Depends(get_supa)):
    window = (datetime.utcnow() - timedelta(days=1)).isoformat()
    data = supa.table('comentarios').select('data_coleta').eq('is_hate', True).gte('data_coleta', window).limit(2000).execute().data or []
    hours = Counter([item['data_coleta'][:13] + ":00:00" for item in data])
    return sorted([{"hora": h, "alertas": v} for h, v in hours.items()], key=lambda x: x['hora'])

@app.get("/api/health")
def health(supa: Client = Depends(get_supa)):
    return {"status": "operational", "db": supa is not None}
