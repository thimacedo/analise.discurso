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

app = FastAPI(title="Sentinela API", version="17.1.0")

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
    return {"status": "online", "engine": "sentinela-api", "version": "17.1.0"}


@app.get("/api/v1/candidatos")
async def get_candidatos(status_monitoramento: str = Query("Ativo")):
    data, _ = await fetch_json(
        "candidatos",
        params={"status_monitoramento": f"eq.{status_monitoramento}", "select": "*", "order": "comentarios_totais_count.desc.nullslast"},
    )
    return data


@app.get("/api/v1/alertas")
async def get_alertas(limit: int = Query(10, ge=1, le=100)):
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


@app.get("/api/v1/summary")
async def get_summary():
    data, _ = await fetch_json("candidatos", params={"select": "comentarios_totais_count,comentarios_odio_count"})
    total_amostra = sum(item.get("comentarios_totais_count", 0) or 0 for item in data)
    total_alertas = sum(item.get("comentarios_odio_count", 0) or 0 for item in data)
    return {
        "total_monitorados": len(data),
        "total_amostra": total_amostra,
        "total_alertas": total_alertas,
        "resiliencia": round(100 - ((total_alertas / total_amostra) * 100), 1) if total_amostra else 100.0,
    }


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
