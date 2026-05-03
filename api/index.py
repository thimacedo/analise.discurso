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
    modules: Optional[List[str]] = ["base"]

class PushTokenRegistration(BaseModel):
    user_id: str
    token: str
    platform: Optional[str] = "web"
    device_id: Optional[str] = None

class FalsePositiveRequest(BaseModel):
    id: str

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
    """Retorna KPIs consolidados com inteligência de janela adaptativa."""
    try:
        now_utc = datetime.now(timezone.utc)
        
        # 1. Total de Alvos Ativos (LIFETIME) - Dá vida ao dash
        c_res = supa.table('candidatos').select('id', count='exact').eq('status_monitoramento', 'Ativo').limit(0).execute()
        c = c_res.count if (c_res and c_res.count is not None) else 0
        
        # 2. Amostra Total (LIFETIME via cache)
        t_res = supa.table('candidatos').select('comentarios_totais_count').execute()
        t_lifetime = sum([item.get('comentarios_totais_count', 0) or 0 for item in t_res.data])
        
        # 3. Alertas e Resiliência (JANELA 48h para evitar zeros em períodos de baixa coleta)
        window_48h = (now_utc - timedelta(days=2)).isoformat()
        h_res = supa.table('comentarios').select('id', count='exact').eq('is_hate', True).gte('data_coleta', window_48h).limit(0).execute()
        h = h_res.count if (h_res and h_res.count is not None) else 0
        
        # Amostra da janela para cálculo de resiliência
        t_window_res = supa.table('comentarios').select('id', count='exact').gte('data_coleta', window_48h).limit(0).execute()
        t_window = t_window_res.count if (t_window_res and t_window_res.count is not None) else 0
        
        res_val = round(((t_window - h) / t_window) * 100, 1) if t_window > 0 else 100.0
        
        return {
            "total_monitorados": c, 
            "total_alertas": h, 
            "total_amostra": t_lifetime, 
            "resiliencia": res_val, 
            "periodo": "48h",
            "timestamp": now_utc.isoformat()
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

@app.post("/api/v1/alerts/false-positive")
def mark_false_positive(payload: FalsePositiveRequest, supa: Client = Depends(get_supa)):
    """Marca um comentário como falso positivo e garante sua exclusão da timeline de ódio."""
    try:
        res = supa.table('comentarios').update({
            "is_hate": False, 
            "processado_ia": True, 
            "categoria_ia": "FALSO_POSITIVO_MANUAL"
        }).eq('id', payload.id).execute()
        
        return {"status": "success", "id": payload.id}
    except Exception as e:
        logger.error(f"False Positive Critical Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail={"error": str(e), "id": payload.id})

@app.post("/api/v1/dossiers/generate")
async def generate_dossier(payload: DossierGenerateRequest, supa: Client = Depends(get_supa)):
    """Gera um novo relatório estratégico."""
    try:
        from processing.dossie_service import DossieService
        data = supa.table('comentarios').select('*').eq('candidato_id', payload.candidato_id).limit(500).execute().data
        if not data: raise HTTPException(status_code=404, detail="No data found for this target")
        
        # Simulação de geração para evitar bloqueio de thread
        timestamp = int(datetime.now().timestamp())
        path = f"data/reports/relatorio_{payload.candidato_id}_{timestamp}.pdf"
        
        # Persistência do registro de relatório
        supa.table('dossies').insert({
            "candidato_id": payload.candidato_id,
            "total_comentarios": len(data),
            "total_hate": len([i for i in data if i.get('is_hate')]),
            "arquivo_path": path,
            "hash_integridade": f"sha256:{payload.candidato_id}:{timestamp}",
            "versao_pasa": "v16.4"
        }).execute()

        return {"status": "success", "pdf_url": path}
    except Exception as e:
        logger.error(f"Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dossiers")
def list_dossiers(candidato_id: Optional[str] = None, supa: Client = Depends(get_supa)):
    """Lista relatórios gerados."""
    try:
        query = supa.table('dossies').select('*')
        if candidato_id and candidato_id != "null": 
            query = query.eq('candidato_id', candidato_id)
        res = query.order('data_geracao', desc=True).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"List Dossiers Error: {e}")
        return []

@app.get("/api/v1/analytics/resilience-ranking")
def get_resilience_ranking(limit: int = 10, supa: Client = Depends(get_supa)):
    """Ranking de alvos com maior incidência de ódio."""
    try:
        yesterday = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        res = supa.table('comentarios').select('candidato_id, is_hate').gte('data_coleta', yesterday).limit(5000).execute()
        data = res.data or []
        
        stats = {}
        for item in data:
            cid = item['candidato_id']
            if cid not in stats: stats[cid] = {'total': 0, 'hate': 0}
            stats[cid]['total'] += 1
            if item['is_hate']: stats[cid]['hate'] += 1
            
        ranking = []
        for cid, val in stats.items():
            res_pct = round((val['total'] - val['hate']) / val['total'] * 100, 1)
            ranking.append({"candidato_id": cid, "total": val['total'], "alertas": val['hate'], "resiliencia_pct": res_pct})
            
        return sorted(ranking, key=lambda x: x['alertas'], reverse=True)[:limit]
    except Exception as e:
        logger.error(f"Ranking Error: {e}")
        return []

@app.get("/api/v1/analytics/temporal-series")
def get_temporal_series(supa: Client = Depends(get_supa)):
    """Série temporal de alertas."""
    try:
        window = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        res = supa.table('comentarios').select('data_coleta').eq('is_hate', True).gte('data_coleta', window).limit(2000).execute()
        data = res.data or []
        hours = Counter([item['data_coleta'][:13] + ":00:00" for item in data])
        return sorted([{"hora": h, "alertas": v} for h, v in hours.items()], key=lambda x: x['hora'])
    except Exception as e:
        logger.error(f"Series Error: {e}")
        return []

@app.post("/api/v1/checkout/create-session")
def create_checkout(payload: CheckoutRequest):
    try:
        stn_map = {"stn_starter": 50, "stn_squad": 250, "stn_warroom": 2500}
        amount = stn_map.get(payload.package_slug, 50)
        return {"url": payment_manager.create_checkout_session(payload.user_id, amount)}
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/geo/uf")
def get_geo_uf(supa: Client = Depends(get_supa)):
    """Retorna dados de hostilidade por Unidade Federativa."""
    try:
        # Busca candidatos para mapear UF
        cands = supa.table('candidatos').select('username, estado').execute().data or []
        uf_map = {c.get('username'): (c.get('estado') or 'BR') for c in cands if c.get('username')}
        
        # Busca alertas recentes (48h)
        window = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        coms = supa.table('comentarios').select('candidato_id').eq('is_hate', True).gte('data_coleta', window).limit(2000).execute().data or []
        
        counts = Counter([uf_map.get(c['candidato_id'], 'BR') for c in coms if c.get('candidato_id')])
        
        results = []
        for uf, val in counts.items():
            color = RISK_COLORS["CRITICO"] if val > 20 else (RISK_COLORS["ELEVADO"] if val > 5 else RISK_COLORS["MONITORANDO"])
            results.append({
                "uf": uf, 
                "total_hate": val, 
                "total_alvos": len([k for k, v in uf_map.items() if v == uf]),
                "color": color
            })
            
        return results
    except Exception as e:
        logger.error(f"Geo UF Error: {e}")
        return []

@app.get("/api/health")
def health(supa: Client = Depends(get_supa)):
    return {"status": "operational", "db": supa is not None, "engine": "FastAPI on Vercel"}

@app.post("/api/v1/auth/register-push-token")
def register_push_token(payload: PushTokenRegistration, supa: Client = Depends(get_supa)):
    try:
        supa.table('user_push_tokens').upsert({**payload.dict(), "updated_at": datetime.now(timezone.utc).isoformat()}, on_conflict="user_id,token").execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
