import hashlib
import hmac
import os
import time
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import Header, HTTPException

load_dotenv()


SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SENTINELA_SUPABASE_KEY") or ""
TOTP_SECRET = os.getenv("SENTINELA_ADMIN_TOTP_SECRET") or ""
APP_ENV = os.getenv("APP_ENV", "development")
CORS_ORIGINS = [origin.strip() for origin in (os.getenv("CORS_ORIGINS") or "*").split(",") if origin.strip()]


def require_env(name: str, value: str) -> str:
    if value:
        return value
    raise HTTPException(status_code=500, detail=f"Variavel obrigatoria ausente: {name}")


def supabase_headers(prefer: Optional[str] = None) -> dict:
    key = require_env("SUPABASE_KEY", SUPABASE_KEY)
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers


async def fetch_json(path: str, *, method: str = "GET", params: Optional[dict] = None, json: Optional[dict] = None,
                     prefer: Optional[str] = None, timeout: float = 20.0) -> tuple[object, httpx.Response]:
    base_url = require_env("SUPABASE_URL", SUPABASE_URL)
    url = f"{base_url}/rest/v1/{path.lstrip('/')}"
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.request(method, url, params=params, json=json, headers=supabase_headers(prefer))
    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    if response.content:
        return response.json(), response
    return None, response


def generate_session_token() -> str:
    key = require_env("SUPABASE_KEY", SUPABASE_KEY)
    exp = int(time.time()) + (2 * 3600)
    payload = str(exp).encode()
    sig = hmac.new(key.encode(), payload, hashlib.sha256).hexdigest()
    return f"{exp}.{sig}"


def verify_session_token(token: Optional[str]) -> None:
    key = require_env("SUPABASE_KEY", SUPABASE_KEY)
    if not token:
        raise HTTPException(status_code=401, detail="Sessao ausente")
    try:
        exp_str, sig = token.split(".")
        expected_sig = hmac.new(key.encode(), exp_str.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            raise HTTPException(status_code=401, detail="Sessao invalida")
        if int(exp_str) < int(time.time()):
            raise HTTPException(status_code=401, detail="Sessao expirada")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Erro de autenticacao") from exc


def get_admin_token(authorization: Optional[str] = Header(None)) -> str:
    token = authorization
    if token and token.lower().startswith("bearer "):
        token = token.split(" ", 1)[1]
    verify_session_token(token)
    return token or ""


def sanitize_username(username: str) -> str:
    return (username or "").strip().replace("@", "").lower()


def safe_origin_list() -> list[str]:
    if CORS_ORIGINS == ["*"]:
        return ["*"]
    return CORS_ORIGINS
