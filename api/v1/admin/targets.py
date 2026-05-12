
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

@app.post("/api/v1/admin/targets")
async def add_target(payload: dict = Body(...), authorization: str = Header(None)):
    verify_session(authorization)
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{SUPABASE_URL}/rest/v1/candidatos",
            headers=get_headers(),
            json={
                "username": payload.get("username"),
                "estado": payload.get("estado"),
                "status_monitoramento": "Ativo"
            }
        )
        return {"status": "created"}
