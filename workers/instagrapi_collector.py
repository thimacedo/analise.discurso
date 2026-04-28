import os
import asyncio
from datetime import datetime
from instagrapi import Client
import httpx
from dotenv import load_dotenv

load_dotenv()

# Credenciais de Elite
IG_USER = "monitoramento.discurso"
IG_PASS = ",F.C6wK89/S)@4V"
SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_sb_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}

async def collect():
    print(f"🔐 [INSTAGRAPI] Autenticando como {IG_USER}...")
    cl = Client()
    try:
        cl.login(IG_USER, IG_PASS)
        print("✅ Login efetuado com sucesso.")
    except Exception as e:
        print(f"❌ Falha no login IG: {e}")
        return

    # Busca alvos
    async with httpx.AsyncClient() as http:
        r = await http.get(f"{SUPABASE_URL}/rest/v1/candidatos?status_monitoramento=eq.Ativo&select=id,username&limit=5", headers=get_sb_headers())
        alvos = r.json()

    for alvo in alvos:
        username = alvo['username']
        c_id = alvo['id']
        print(f"📸 Coletando posts de @{username}...")
        
        try:
            user_id = cl.user_id_from_username(username)
            medias = cl.user_medias(user_id, 2) # Últimos 2 posts
            
            payload = []
            for media in medias:
                comments = cl.media_comments(media.id, 10)
                for c in comments:
                    payload.append({
                        "candidato_id": c_id,
                        "texto_bruto": c.text,
                        "autor_username": c.user.username,
                        "fonte_coleta": "Instagrapi/Direct",
                        "processado_ia": False
                    })
            
            if payload:
                async with httpx.AsyncClient() as http:
                    res = await http.post(f"{SUPABASE_URL}/rest/v1/comentarios", headers=get_sb_headers(), json=payload)
                    print(f"📊 {len(payload)} evidências reais salvas para @{username} (Status: {res.status_code})")
            
            await asyncio.sleep(10) # Delay anti-ban
        except Exception as e:
            print(f"⚠️ Erro em @{username}: {e}")

if __name__ == '__main__':
    asyncio.run(collect())
