from fastapi import FastAPI, HTTPException, Body, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
import os
import sys
from dotenv import load_dotenv
from collections import Counter
import traceback
import logging
from datetime import datetime, timedelta, timezone
import stripe

# Ajuste de path para imports locais (Vercel compliance)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from stripe_service import payment_manager
except ImportError:
    # Fallback se rodar da raiz
    from api.stripe_service import payment_manager

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
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

def get_supa() -> Client:
    """Dependency para obter cliente Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=500, detail="Database credentials (SUPABASE_URL/KEY) missing in environment")
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Supabase Client Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to Supabase")

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

@app.get("/api/v1/summary")
def summary(supa: Client = Depends(get_supa)):
    """Retorna KPIs consolidados (Janela 24h) com performance Diamond."""
    try:
        # Usa timezone-aware datetime para compatibilidade máxima
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        
        # 1. Total de Alvos Ativos no Período (Contagem de alvos distintos com comentários)
        # Hack: Contamos alvos únicos via RPC ou processando pequena amostra se o PostgREST limitar
        c_res = supa.table('comentarios').select('candidato_id', count='exact').gte('data_coleta', yesterday).limit(1000).execute()
        distinct_targets = set([item['candidato_id'] for item in c_res.data if item.get('candidato_id')])
        c = len(distinct_targets)
        
        # 2. Amostra Total (24h)
        t = c_res.count if c_res and c_res.count is not None else 0
        
        # 3. Total de Alertas (24h)
        h_res = supa.table('comentarios').select('id', count='exact').eq('is_hate', True).gte('data_coleta', yesterday).limit(0).execute()
        h = h_res.count if h_res and h_res.count is not None else 0
        
        # 4. Cálculo de Resiliência (24h)
        res_val = round((t - h) / t * 100, 1) if t > 0 else 100
        
        return {
            "total_monitorados": c, 
            "total_alertas": h, 
            "total_amostra": t, 
            "resiliencia": res_val, 
            "periodo": "24h",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Summary KPI Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/targets")
def get_targets(limit: int = 50, supa: Client = Depends(get_supa)):
    try:
        # Busca candidatos ativos
        candidates_res = supa.table('candidatos').select('*').eq('status_monitoramento', 'Ativo').execute()
        candidates = candidates_res.data or []
        
        # Busca ódio recente para enriquecer
        h_res = supa.table('comentarios').select('candidato_id, categoria_ia').eq('is_hate', True).limit(2000).execute()
        h_data = h_res.data or []
        
        counts = Counter([h['candidato_id'] for h in h_data])
        breakdowns = {}
        for h in h_data:
            cid, cat = h['candidato_id'], h['categoria_ia'] or 'OUTROS'
            if cid not in breakdowns: breakdowns[cid] = Counter()
            breakdowns[cid][cat] += 1
        
        enriched = []
        for item in candidates:
            cid = item.get('username')
            item['comentarios_odio_count'] = counts.get(cid, 0)
            score, nivel, color = calculate_risk(item)
            enriched.append({
                **item, 
                "score_risco": score, 
                "nivel_risco": nivel, 
                "color": color, 
                "breakdown": dict(breakdowns.get(cid, {}))
            })
            
        return sorted(enriched, key=lambda x: x.get('comentarios_odio_count', 0), reverse=True)[:limit]
    except Exception as e:
        logger.error(f"Targets Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/alerts/active")
def get_active_alerts(limit: int = 20, supa: Client = Depends(get_supa)):
    try:
        res = supa.table('comentarios').select('*, candidatos(username)').eq('is_hate', True).order('data_coleta', desc=True).limit(limit).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Alerts Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/checkout/create-session")
def create_checkout(payload: CheckoutRequest):
    try:
        stn_map = {"stn_starter": 50, "stn_squad": 250, "stn_warroom": 2500}
        amount = stn_map.get(payload.package_slug, 50)
        return {"url": payment_manager.create_checkout_session(payload.user_id, amount)}
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health(supa: Client = Depends(get_supa)):
    return {"status": "operational", "db": supa is not None, "engine": "FastAPI on Vercel"}

# Endpoints secundários e Auth mantidos para compatibilidade...
@app.post("/api/v1/auth/register-push-token")
def register_push_token(payload: PushTokenRegistration, supa: Client = Depends(get_supa)):
    try:
        supa.table('user_push_tokens').upsert({**payload.dict(), "updated_at": datetime.now(timezone.utc).isoformat()}, on_conflict="user_id,token").execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
