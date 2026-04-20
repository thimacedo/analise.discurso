import os
import asyncio
import httpx
import time
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from groq import Groq

app = FastAPI()

# --- CONFIGURAÇÃO RESILIENTE ---
def get_groq_client():
    key = os.environ.get("GROQ_API_KEY")
    if not key: return None
    try:
        return Groq(api_key=key)
    except: return None

# Headers
HEADERS_IG = {
    "User-Agent": "Instagram 123.0.0.21.114 (iPhone; iOS 13_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+",
    "Cookie": os.environ.get("INSTAGRAM_SESSIONID", ""),
    "x-ig-app-id": "936619743392459"
}

AI_PROMPT = "Analise o discurso de ódio político. Retorne JSON: {is_hate:bool, categoria:str, justificativa:str}"

async def analyze_with_groq(text: str):
    client = get_groq_client()
    if not client: return None
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": AI_PROMPT}, {"role": "user", "content": text}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(completion.choices[0].message.content)
    except: return None

@app.get("/api/status")
async def status():
    return {
        "status": "online", 
        "has_groq": os.environ.get("GROQ_API_KEY") is not None,
        "has_ig": os.environ.get("INSTAGRAM_SESSIONID") is not None
    }

@app.get("/api/collect")
@app.get("/api/main")
async def collect_handler():
    start_time = time.time()
    stats = {"status": "success", "synced": 0, "analyzed": 0}
    
    # 🧪 Early Exit if Env is missing
    sb_url = os.environ.get("SUPABASE_URL")
    sb_key = os.environ.get("SUPABASE_KEY")
    if not sb_url or not sb_key:
        return {"error": "Supabase Credentials Missing"}

    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        try:
            # Logic stays clean and decoupled
            target_id = "69168962266"
            url_ig = f"https://www.instagram.com/api/v1/friendships/{target_id}/following/"
            resp = await client.get(url_ig, headers=HEADERS_IG)
            
            if resp.status_code != 200:
                return {"error": "Instagram Auth Fail", "code": resp.status_code}
            
            # ... process items (simplified for startup test)
            return {"status": "success", "message": "Service reached IG successfully"}

        except Exception as e:
            return {"status": "error", "message": str(e)}
