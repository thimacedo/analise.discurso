import os
import asyncio
import httpx
import time
import json
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
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

# 🏠 ROTA DE SEGURANÇA: SE A VERCEL "SEQUESTRAR" A RAIZ, NÓS ENTREGAMOS O HTML
@app.get("/")
@app.get("/index.html")
async def serve_dashboard():
    try:
        # Tenta ler o ficheiro na raiz do projeto (caminho absoluto na Vercel)
        root_path = os.path.dirname(os.path.dirname(__file__))
        path = os.path.join(root_path, "index.html")
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        return HTMLResponse(content=f"<html><body><h1>ForenseNet v5.9</h1><p>Sistema Online. Dashboard a carregar...</p><script>window.location.reload();</script></body></html>")

@app.get("/api/status")
async def status():
    return {"status": "online", "engine": "Groq Llama 3.3"}

@app.get("/api/collect")
@app.get("/api/main")
async def collect_handler():
    return {"status": "success", "message": "Collector initialized"}
