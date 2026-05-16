import os
import httpx
import pyotp
import time
import hmac
import hashlib
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TOTP_SECRET = os.getenv("SENTINELA_ADMIN_TOTP_SECRET")

def generate_session_token():
    exp = int(time.time()) + (2 * 3600)
    msg = str(exp).encode()
    sig = hmac.new(SUPABASE_KEY.encode(), msg, hashlib.sha256).hexdigest()
    return f"{exp}.{sig}"

@app.post("/api/v1/admin/login")
async def admin_login(payload: dict = Body(...)):
    code = payload.get("code")
    if not TOTP_SECRET:
        raise HTTPException(status_code=500, detail="Auth not configured")
    
    totp = pyotp.TOTP(TOTP_SECRET)
    if totp.verify(code):
        return {"token": generate_session_token(), "expires_in": 7200}
    else:
        raise HTTPException(status_code=401, detail="Código inválido")
