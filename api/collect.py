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

# Credenciais do Ambiente
SESSION_ID = os.environ.get("INSTAGRAM_SESSIONID")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
TARGET_ID = "69168962266" # monitoramento.discurso

client_groq = Groq(api_key=GROQ_KEY) if GROQ_KEY else None

HEADERS_IG = {
    "User-Agent": "Instagram 123.0.0.21.114 (iPhone; iOS 13_3; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/420+",
    "Cookie": f"sessionid={SESSION_ID}",
    "x-ig-app-id": "936619743392459"
}

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

async def analyze_with_groq(text: str):
    if not client_groq: return None
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Analise o discurso de ódio político. Retorne JSON: {is_hate:bool, categoria:str, justificativa:str}"},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(completion.choices[0].message.content)
    except: return None

@app.get("/")
@app.get("/api/collect")
async def collect_handler():
    start_time = time.time()
    max_duration = 8.5 # Segurança para Vercel (Hobby limit 10s)
    
    stats = {"status": "success", "synced": 0, "analyzed": 0, "execution": 0}
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        try:
            # 1. Alvos
            resp = await client.get(f"https://www.instagram.com/api/v1/friendships/{TARGET_ID}/following/", headers=HEADERS_IG)
            if resp.status_code != 200: return JSONResponse(status_code=resp.status_code, content={"error": "Auth Fail"})
            
            targets = resp.json().get("users", [])[:3] # Start pequeno para estabilidade
            payload = []

            for user in targets:
                if time.time() - start_time > max_duration: break
                
                resp_feed = await client.get(f"https://www.instagram.com/api/v1/feed/user/{user['pk']}/", headers=HEADERS_IG)
                if resp_feed.status_code != 200: continue
                
                posts = resp_feed.json().get("items", [])[:1]
                for post in posts:
                    resp_comm = await client.get(f"https://www.instagram.com/api/v1/media/{post['pk']}/comments/", headers=HEADERS_IG)
                    if resp_comm.status_code != 200: continue
                    
                    comments = resp_comm.json().get("comments", [])[:5]
                    for c in comments:
                        if time.time() - start_time > max_duration: break
                        
                        ai_res = await analyze_with_groq(c["text"])
                        payload.append({
                            "id_externo": str(c["pk"]),
                            "candidato_id": user["username"],
                            "post_id": str(post["pk"]),
                            "autor_username": c["user"]["username"],
                            "texto_bruto": c["text"],
                            "data_publicacao": datetime.fromtimestamp(c["created_at"]).isoformat(),
                            "data_coleta": datetime.now().isoformat(),
                            "is_hate": ai_res.get("is_hate", False) if ai_res else False,
                            "categoria_ia": ai_res.get("categoria", "Neutro") if ai_res else "Erro",
                            "justificativa_ia": ai_res.get("justificativa", "") if ai_res else "",
                            "processado_ia": True if ai_res else False
                        })
                        if ai_res: stats["analyzed"] += 1

            # 2. Salvar
            if payload:
                await client.post(f"{SUPABASE_URL}/rest/v1/comentarios", json=payload, headers=HEADERS_SB)
                stats["synced"] = len(payload)

        except Exception as e:
            return {"status": "error", "msg": str(e)}

    stats["execution"] = round(time.time() - start_time, 2)
    return stats
