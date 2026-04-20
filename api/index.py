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

# --- CONFIGURAÇÃO ---
def get_groq_client():
    key = os.environ.get("GROQ_API_KEY")
    if not key: return None
    try: return Groq(api_key=key)
    except: return None

HEADERS_IG = {
    "User-Agent": "Instagram 123.0.0.21.114 (iPhone; iOS 13_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+",
    "Cookie": os.environ.get("INSTAGRAM_SESSIONID", ""),
    "x-ig-app-id": "936619743392459"
}

@app.get("/api/status")
async def status():
    return {"status": "online", "engine": "Groq Llama 3.3"}

@app.get("/api/collect")
async def collect_handler():
    # Only background sync logic here
    return {"status": "success", "message": "Collector initialized"}
