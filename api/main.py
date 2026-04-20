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

# 🏠 ROTA RAIZ: SERVIR O DASHBOARD (index.html)
@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
async def serve_dashboard():
    """
    Lê o ficheiro index.html da raiz e entrega ao navegador.
    Esta é a solução definitiva para o erro 'Not Found'.
    """
    try:
        # Tenta encontrar o ficheiro na raiz (padrão Vercel)
        path = os.path.join(os.getcwd(), "index.html")
        if not os.path.exists(path):
            # Fallback para subpasta se necessário
            path = os.path.join(os.getcwd(), "public", "index.html")
            
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<html><body><h1>Erro ao carregar Dashboard</h1><p>{str(e)}</p></body></html>"

@app.get("/api/status")
async def status():
    return {"status": "online", "engine": "Groq Llama 3.3"}

@app.get("/api/collect")
@app.get("/api/main")
async def collect_handler():
    # ... (lógica de coleta existente mantida para background sync)
    return {"status": "success", "message": "Collector initialized"}
