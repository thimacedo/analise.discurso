
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import httpx
import time
import hmac
import hashlib
from fastapi import FastAPI, Header, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def verify_session(token: Optional[str]):
    if not token:
        raise HTTPException(status_code=401, detail="Sessão ausente")
    try:
        exp_str, sig = token.split(".")
        msg = exp_str.encode()
        expected_sig = hmac.new(SUPABASE_KEY.encode(), msg, hashlib.sha256).hexdigest()
        if sig != expected_sig:
            raise HTTPException(status_code=401, detail="Sessão inválida")
        if int(exp_str) < int(time.time()):
            raise HTTPException(status_code=401, detail="Sessão expirada")
        return True
    except:
        raise HTTPException(status_code=401, detail="Erro de autenticação")

def get_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

@app.get("/api/v1/admin/comments/review")
async def review_comments(is_hate: bool = True, authorization: str = Header(None)):
    verify_session(authorization)
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/comentarios?is_hate=eq.{str(is_hate).lower()}&select=*,candidatos(username)&limit=50&order=data_coleta.desc", headers=get_headers())
        data = r.json()
        return [{
            "id": c.get('id'),
            "texto_bruto": c.get('texto_bruto'),
            "candidato_id": c.get('candidatos', {}).get('username', '???'),
            "is_hate": c.get('is_hate')
        } for c in data]

@app.patch("/api/v1/admin/comments/{comment_id}")
async def update_comment_status(comment_id: int, payload: dict = Body(...), authorization: str = Header(None)):
    verify_session(authorization)
    async with httpx.AsyncClient() as client:
        await client.patch(
            f"{SUPABASE_URL}/rest/v1/comentarios?id=eq.{comment_id}",
            headers=get_headers(),
            json={"is_hate": payload.get("is_hate")}
        )
        return {"status": "updated"}
