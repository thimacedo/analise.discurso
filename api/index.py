from typing import Optional

import pyotp
from fastapi import Body, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.common import (
    TOTP_SECRET,
    fetch_json,
    generate_session_token,
    get_admin_token,
    safe_origin_list,
    sanitize_username,
)

app = FastAPI(title="Sentinela API", version="19.1.1")

allow_origins = safe_origin_list()
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/status")
def status():
    return {"status": "online", "engine": "sentinela-api", "version": "19.1.1"}


@app.get("/api/v1/candidatos")
async def get_candidatos(status_monitoramento: str = Query("Ativo")):
    try:
        # Tenta a view avançada com score
        data, _ = await fetch_json(
            "v_candidato_score",
            params={"status_monitoramento": f"eq.{status_monitoramento}", "select": "*", "order": "score_risco.desc"},
        )
        return data
    except Exception:
        # Fallback para tabela base se a view nao existir
        try:
            data, _ = await fetch_json(
                "candidatos",
                params={"status_monitoramento": f"eq.{status_monitoramento}", "select": "*"},
            )
            return data
        except Exception:
            return []


@app.get("/api/v1/alertas")
async def get_alertas(limit: int = Query(10, ge=1, le=100)):
    try:
        data, _ = await fetch_json(
            "comentarios",
            params={
                "is_hate": "eq.true",
                "select": "*,candidatos(username)",
                "order": "data_coleta.desc",
                "limit": limit,
            },
        )
        return data
    except Exception:
        return []


@app.get("/api/v1/summary")
async def get_summary():
    try:
        # Dados atuais
        try:
            data, _ = await fetch_json("candidatos", params={"select": "comentarios_totales_count,comentarios_odio_count,estado"})
        except Exception:
            # Fallback para nomes de colunas antigos se houver
            data, _ = await fetch_json("candidatos", params={"select": "comentarios_totais_count,comentarios_odio_count,estado"})
            
        total_amostra = sum(item.get("comentarios_totales_count", 0) or item.get("comentarios_totais_count", 0) or 0 for item in data)
        total_alertas = sum(item.get("comentarios_odio_count", 0) or 0 for item in data)
        uf_count = len(set(item.get("estado") for item in data if item.get("estado")))
        
        # Dados de tendência (últimos 30 dias)
        trends = []
        try:
            trends, _ = await fetch_json(
                "metricas_diarias",
                params={"select": "total_coletado,total_hate,resiliencia", "order": "data.desc", "limit": "30"}
            )
        except Exception: pass
        
        sparklines = {
            "monitorados": [d["total_coletado"] for d in reversed(trends[:12])] if len(trends) >= 12 else [],
            "hate": [d["total_hate"] for d in reversed(trends[:12])] if len(trends) >= 12 else [],
            "total": [d["total_coletado"] for d in reversed(trends[:12])] if len(trends) >= 12 else [],
            "resiliencia": [d["resiliencia"] for d in reversed(trends[:12])] if len(trends) >= 12 else [],
        }
        
        # Cálculo de tendência
        hate_trend = 0
        res_trend = 0
        if len(trends) >= 14:
            recent_hate = sum(d["total_hate"] for d in trends[:7]) / 7
            prev_hate = sum(d["total_hate"] for d in trends[7:14]) / 7
            hate_trend = round(((recent_hate - prev_hate) / prev_hate) * 100, 1) if prev_hate > 0 else 0
            
            recent_res = sum(d["resiliencia"] for d in trends[:7]) / 7
            prev_res = sum(d["resiliencia"] for d in trends[7:14]) / 7
            res_trend = round(recent_res - prev_res, 1)
        
        # PASA breakdown rápido
        pasa_dict = {}
        try:
            pasa, _ = await fetch_json("v_pasa_breakdown", params={"select": "categoria_ia,total", "limit": "6"})
            pasa_dict = {item["categoria_ia"]: item["total"] for item in pasa}
        except Exception: pass
        
        return {
            "total_monitorados": len(data),
            "total_amostra": total_amostra,
            "total_alertas": total_alertas,
            "resiliencia": round(100 - ((total_alertas / total_amostra) * 100), 1) if total_amostra and total_alertas else 100.0,
            "uf_cobertos": uf_count,
            "pasa_breakdown": pasa_dict,
            "trends": {
                "hate_trend_pct": hate_trend,
                "resiliencia_trend_pct": res_trend,
            },
            "sparklines": sparklines,
        }
    except Exception as e:
        return {
            "total_monitorados": 0, "total_amostra": 0, "total_alertas": 0, "resiliencia": 100.0,
            "uf_cobertos": 0, "pasa_breakdown": {}, "trends": {"hate_trend_pct": 0, "resiliencia_trend_pct": 0},
            "sparklines": {"monitorados": [], "hate": [], "total": [], "resiliencia": []},
            "error": str(e)
        }


@app.get("/api/v1/trends")
async def get_trends(days: int = Query(30, ge=7, le=365)):
    try:
        data, _ = await fetch_json(
            "metricas_diarias",
            params={
                "select": "data,total_coletado,total_hate,total_neutro,resiliencia,pasa_breakdown,uf_breakdown",
                "order": "data.asc",
                "limit": days
            }
        )
        return data
    except Exception:
        return []


@app.get("/api/v1/pasa/breakdown")
async def get_pasa_breakdown():
    try:
        # Busca agregação real da tabela de comentários (dados persistidos pelo orquestrador)
        query = "select=categoria_ia,count=exact"
        # Nota: PostgREST aggregate functions dependem da versão do Supabase. 
        # Como fallback, usamos a view materializada se existir ou retornamos dados processados.
        data, _ = await fetch_json("v_pasa_breakdown", params={"select": "*"})
        
        PASA_CONFIG = {
            "ODIO_IDENTITARIO":    {"label": "Ódio Identitário",   "color": "#ef4444", "icon": "users"},
            "VIOLENCIA_GENERO":    {"label": "Violência de Gênero","color": "#ec4899", "icon": "shield-alert"},
            "AMEACA":              {"label": "Ameaça",             "color": "#f97316", "icon": "alert-octagon"},
            "INSULTO_AD_HOMINEM":  {"label": "Insulto Ad Hominem", "color": "#f59e0b", "icon": "swords"},
            "ATAQUE_INSTITUCIONAL":{"label": "Ataque Institucional","color": "#8b5cf6", "icon": "landmark"},
            "RIGOR_CRIMINAL":      {"label": "Rigor Criminal",     "color": "#06b6d4", "icon": "scale"},
        }
        
        return [{
            **item,
            "label": PASA_CONFIG.get(item["categoria_ia"], {}).get("label", item["categoria_ia"]),
            "color": PASA_CONFIG.get(item["categoria_ia"], {}).get("color", "#64748b"),
            "icon": PASA_CONFIG.get(item["categoria_ia"], {}).get("icon", "help-circle"),
        } for item in data]
    except Exception:
        # Fallback manual via RPC ou contagem direta se a view falhar
        return []


@app.get("/api/v1/geo/uf")
async def get_geo_uf():
    try:
        data, _ = await fetch_json("mv_agregacao_uf", params={"select": "*", "order": "total_hate.desc"})
        
        RISK_COLORS = {
            "CRITICO": "#ef4444",
            "ELEVADO": "#f59e0b",
            "MONITORANDO": "#06b6d4",
            "CONTROLADO": "#10b981",
        }
        
        return [{
            **item,
            "color": RISK_COLORS.get(item["nivel_risco"], "#64748b"),
        } for item in data]
    except Exception:
        return []


@app.get("/api/v1/networks")
async def get_networks():
    try:
        data, _ = await fetch_json(
            "redes_coordenadas",
            params={
                "select": "*",
                "order": "severidade.desc",
                "status": "neq.DESATIVADA",
            }
        )
        return data
    except Exception:
        return []


@app.get("/api/v1/alerts/active")
async def get_active_alerts(limit: int = Query(20, ge=1, le=100)):
    try:
        data, _ = await fetch_json(
            "alertas_ativos",
            params={
                "select": "*",
                "status": "eq.ATIVO",
                "order": "created_at.desc",
                "limit": limit,
            }
        )
        return data
    except Exception:
        try:
            # Fallback para alertas brutos se a tabela nova nao existir
            data, _ = await fetch_json(
                "comentarios",
                params={"is_hate": "eq.true", "limit": limit, "order": "data_coleta.desc"}
            )
            return data
        except Exception:
            return []


@app.get("/api/v1/targets")
async def get_targets(
    search: str = Query(None),
    group_by: str = Query("score"),
    limit: int = Query(50, ge=1, le=200),
):
    try:
        params = {
            "select": "*",
            "order": "score_risco.desc" if group_by == "score" else "estado.asc,nome_completo.asc",
            "limit": limit,
        }
        if search:
            params["or"] = f"(username.ilike.*{search}*,nome_completo.ilike.*{search}*,estado.ilike.*{search}*)"
        
        data, _ = await fetch_json("v_candidato_score", params=params)
        
        RISK_COLORS = {
            "CRITICO": "#ef4444",
            "ELEVADO": "#f59e0b",
            "MONITORANDO": "#06b6d4",
            "CONTROLADO": "#10b981",
        }
        
        return [{
            **item,
            "color": RISK_COLORS.get(item.get("nivel_risco", ""), "#64748b"),
        } for item in data]
    except Exception:
        # Fallback para tabela base
        try:
            params = {"select": "*", "limit": limit}
            data, _ = await fetch_json("candidatos", params=params)
            return data
        except Exception:
            return []


@app.post("/api/v1/admin/login")
async def admin_login(payload: dict = Body(...)):
    if not TOTP_SECRET:
        raise HTTPException(status_code=500, detail="Auth not configured")
    code = str(payload.get("code") or "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="Codigo obrigatorio")
    totp = pyotp.TOTP(TOTP_SECRET)
    if not totp.verify(code):
        raise HTTPException(status_code=401, detail="Codigo invalido")
    return {"token": generate_session_token(), "expires_in": 7200}


@app.get("/api/v1/admin/comments/review")
async def review_comments(
    is_hate: bool = True,
    limit: int = Query(50, ge=1, le=200),
    _token: str = Depends(get_admin_token),
):
    data, _ = await fetch_json(
        "comentarios",
        params={
            "is_hate": f"eq.{str(is_hate).lower()}",
            "select": "*,candidatos(username)",
            "limit": limit,
            "order": "data_coleta.desc",
        },
    )
    return [{
        "id": item.get("id"),
        "texto_bruto": item.get("texto_bruto"),
        "candidato_id": item.get("candidatos", {}).get("username"),
        "is_hate": item.get("is_hate"),
        "categoria_ia": item.get("categoria_ia"),
        "data_coleta": item.get("data_coleta"),
    } for item in data]


@app.patch("/api/v1/admin/comments/{comment_id}")
async def update_comment_status(
    comment_id: int,
    payload: dict = Body(...),
    _token: str = Depends(get_admin_token),
):
    body = {"is_hate": bool(payload.get("is_hate"))}
    categoria = payload.get("categoria_ia")
    if categoria:
        body["categoria_ia"] = categoria
    justificativa = payload.get("justificativa")
    if justificativa:
        body["justificativa"] = justificativa
    _, _response = await fetch_json(
        "comentarios",
        method="PATCH",
        params={"id": f"eq.{comment_id}"},
        json=body,
        prefer="return=representation",
    )
    return {"status": "updated", "comment_id": comment_id}


@app.post("/api/v1/admin/targets")
async def add_target(
    payload: dict = Body(...),
    _token: str = Depends(get_admin_token),
):
    username = sanitize_username(payload.get("username"))
    if not username:
        raise HTTPException(status_code=400, detail="Username obrigatorio")
    body = {
        "username": username,
        "nome_completo": payload.get("nome_completo") or payload.get("nome") or "Nao informado",
        "cargo": payload.get("cargo") or "Monitorado",
        "estado": payload.get("estado") or "BR",
        "status_monitoramento": payload.get("status_monitoramento") or "Ativo",
    }
    data, _ = await fetch_json(
        "candidatos",
        method="POST",
        json=body,
        prefer="resolution=merge-duplicates,return=representation",
    )
    return {"status": "created", "target": data[0] if isinstance(data, list) and data else body}


@app.patch("/api/v1/admin/targets/{username}")
async def update_target(
    username: str,
    payload: dict = Body(...),
    _token: str = Depends(get_admin_token),
):
    clean_username = sanitize_username(username)
    body = {key: value for key, value in payload.items() if value is not None}
    if "username" in body:
        body["username"] = sanitize_username(body["username"])
    _, _ = await fetch_json(
        "candidatos",
        method="PATCH",
        params={"username": f"eq.{clean_username}"},
        json=body,
        prefer="return=representation",
    )
    return {"status": "updated", "username": clean_username}

# ==========================================
# MÓDULO DE PAGAMENTO: STRIPE (v19.6.0)
# ==========================================
from api.stripe_service import create_checkout_session, verify_webhook_signature
from fastapi import Request, Header

# Mapeamento de Preços para Tokens
PRICE_TO_TOKENS = {
    os.getenv("STRIPE_STARTER_PRICE_ID"): 1,
    os.getenv("STRIPE_SQUAD_PRICE_ID"): 4,
    os.getenv("STRIPE_WARROOM_PRICE_ID"): 15,
}

@app.post("/api/v1/checkout/create-session")
async def create_checkout_session_route(payload: dict = Body(...), authorization: str = Header(None)):
    # Simulação de extração de user_id do JWT (idealmente via middleware ou helper)
    # Por enquanto, confiamos no payload ou extraímos 'sub' se for JWT real
    user_id = payload.get("user_id") 
    price_id = payload.get("price_id")
    package_slug = payload.get("package_slug", "custom")

    if not price_id or not user_id:
        raise HTTPException(status_code=400, detail="Faltam dados obrigatorios")

    try:
        url = create_checkout_session(user_id, package_slug, price_id)
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/webhooks/stripe")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    payload = await request.body()
    event = verify_webhook_signature(payload, stripe_signature)
    
    if not event:
        raise HTTPException(status_code=400, detail="Webhook Error: Invalid Signature")

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('metadata', {}).get('user_id')
        price_id = session.get('metadata', {}).get('price_id')
        
        token_amount = PRICE_TO_TOKENS.get(price_id, 0)
        
        if user_id and token_amount > 0:
            # Chamada atômica ao Supabase via RPC
            await fetch_json(
                "rpc/process_stn_transaction",
                method="POST",
                json={
                    "p_user_id": user_id,
                    "p_amount": token_amount,
                    "p_type": "PURCHASE",
                    "p_session_id": session.get('id'),
                    "p_metadata": {"price_id": price_id}
                }
            )
    
    return {"status": "success"}

