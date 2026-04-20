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

# Credenciais (Puxadas DIRETAMENTE das ENV da Vercel)
SESSION_ID = os.environ.get("INSTAGRAM_SESSIONID")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GROQ_KEY = os.environ.get("GROQ_API_KEY")
TARGET_ID = "69168962266"

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

AI_PROMPT = """Analise este comentário político para fins periciais. 
Retorne JSON: {is_hate: bool, categoria: str, justificativa: str, is_sarcastic: bool}"""

async def analyze_with_groq(text: str):
    if not client_groq: return None
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": AI_PROMPT}, {"role": "user", "content": text}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return json.loads(completion.choices[0].message.content)
    except: return None

@app.get("/api/collect")
async def collect_handler():
    start_time = time.time()
    max_duration = 9.0 # Vercel limit is 10s
    
    stats = {"status": "success", "synced": 0, "analyzed": 0, "execution": 0}
    
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        try:
            # 1. Buscar alvos
            url_following = f"https://www.instagram.com/api/v1/friendships/{TARGET_ID}/following/"
            resp = await client.get(url_following, headers=HEADERS_IG)
            if resp.status_code != 200: return {"error": "Auth Fail", "code": resp.status_code}
            
            targets = resp.json().get("users", [])[:5] # Limite para serverless
            payload = []

            for user in targets:
                if time.time() - start_time > max_duration: break
                
                # 2. Buscar feed
                url_feed = f"https://www.instagram.com/api/v1/feed/user/{user['pk']}/"
                resp_feed = await client.get(url_feed, headers=HEADERS_IG)
                if resp_feed.status_code != 200: continue
                
                posts = resp_feed.json().get("items", [])[:1] # Apenas o mais recente para velocidade
                
                for post in posts:
                    # 3. Buscar comentários
                    url_comm = f"https://www.instagram.com/api/v1/media/{post['pk']}/comments/"
                    resp_comm = await client.get(url_comm, headers=HEADERS_IG)
                    if resp_comm.status_code != 200: continue
                    
                    comments = resp_comm.json().get("comments", [])[:10]
                    for c in comments:
                        if time.time() - start_time > max_duration: break
                        
                        text = c["text"]
                        # 🧠 Perícia Groq em Tempo Real
                        ai_res = await analyze_with_groq(text)
                        
                        payload.append({
                            "id_externo": str(c["pk"]),
                            "candidato_id": user["username"],
                            "post_id": str(post["pk"]),
                            "autor_username": c["user"]["username"],
                            "texto_bruto": text,
                            "data_publicacao": datetime.fromtimestamp(c["created_at"]).isoformat(),
                            "data_coleta": datetime.now().isoformat(),
                            "is_hate": ai_res.get("is_hate", False) if ai_res else False,
                            "categoria_ia": ai_res.get("categoria", "Não Analisado") if ai_res else "Erro",
                            "justificativa_ia": ai_res.get("justificativa", "") if ai_res else "",
                            "processado_ia": True if ai_res else False
                        })
                        if ai_res: stats["analyzed"] += 1

            # 4. Save
            if payload:
                url_sb = f"{SUPABASE_URL}/rest/v1/comentarios"
                await client.post(url_sb, json=payload, headers=HEADERS_SB)
                stats["synced"] = len(payload)

        except Exception as e:
            return {"status": "error", "msg": str(e)}

    stats["execution"] = round(time.time() - start_time, 2)
    return stats
