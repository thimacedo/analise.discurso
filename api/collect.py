import os
import asyncio
import httpx
import time
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

# Configurações do Ambiente (Injetadas pela Vercel)
SESSION_ID = os.getenv("INSTAGRAM_SESSIONID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TARGET_ID = "69168962266" # Monitor ID: monitoramento.discurso

# Headers para emular cliente mobile e evitar bloqueios
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

@app.get("/api/collect")
async def collect_handler():
    """
    Coletor Serverless leve para Vercel.
    Executa um ciclo rápido de coleta para monitorar novos ataques.
    """
    start_time = time.time()
    max_duration = 8.5  # Limite Hobby da Vercel é 10s.
    
    stats = {
        "status": "success",
        "synced_comments": 0,
        "targets_processed": 0,
        "execution_time": 0,
        "errors": []
    }
    
    if not SESSION_ID or not SUPABASE_URL:
        return {"error": "Missing environment variables (SESSION_ID/SUPABASE_URL)"}

    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        try:
            # 1. Buscar alvos monitorados
            url_following = f"https://www.instagram.com/api/v1/friendships/{TARGET_ID}/following/"
            resp = await client.get(url_following, headers=HEADERS_IG)
            
            if resp.status_code != 200:
                return JSONResponse(status_code=resp.status_code, content={"error": "Instagram Session Expired", "status": resp.status_code})
            
            targets = resp.json().get("users", [])
            all_comments = []

            for user in targets:
                if time.time() - start_time > max_duration: break
                
                user_id = user["pk"]
                username = user["username"]
                
                # 2. Buscar feed rápido
                url_feed = f"https://www.instagram.com/api/v1/feed/user/{user_id}/"
                try:
                    resp_feed = await client.get(url_feed, headers=HEADERS_IG)
                    if resp_feed.status_code != 200: continue
                    
                    items = resp_feed.json().get("items", [])[:2] # Apenas os 2 últimos no serverless para ser rápido
                    
                    for post in items:
                        if time.time() - start_time > max_duration: break
                        media_id = post["pk"]
                        
                        # 3. Buscar comentários
                        url_comments = f"https://www.instagram.com/api/v1/media/{media_id}/comments/"
                        resp_comm = await client.get(url_comments, headers=HEADERS_IG)
                        if resp_comm.status_code != 200: continue
                        
                        comments = resp_comm.json().get("comments", [])[:20]
                        for c in comments:
                            all_comments.append({
                                "id_externo": str(c["pk"]),
                                "candidato_id": username,
                                "post_id": str(media_id),
                                "autor_username": c["user"]["username"],
                                "texto_bruto": c["text"],
                                "data_publicacao": datetime.fromtimestamp(c["created_at"]).isoformat(),
                                "likes": c.get("comment_like_count", 0),
                                "data_coleta": datetime.now().isoformat(),
                                "processado_ia": False
                            })
                    stats["targets_processed"] += 1
                except: continue

            # 4. UPSERT no Supabase
            if all_comments:
                url_sb = f"{SUPABASE_URL}/rest/v1/comentarios"
                resp_sb = await client.post(url_sb, json=all_comments, headers=HEADERS_SB)
                stats["synced_comments"] = len(all_comments) if resp_sb.status_code in [200, 201] else 0

        except Exception as e:
            return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

    stats["execution_time"] = round(time.time() - start_time, 2)
    return stats
