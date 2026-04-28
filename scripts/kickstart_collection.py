import os
import asyncio
import httpx
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Credenciais do .env
SESSION_ID = os.getenv("INSTAGRAM_SESSIONID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GRO_KEY = os.getenv("GROQ_API_KEY")

client_groq = Groq(api_key=GRO_KEY)

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

async def analyze(text):
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Analise como perito criminal. Retorne JSON: {is_hate:bool, categoria:str, justificativa:str}"},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except: return None

async def kickstart():
    print("🚀 INICIANDO COLETA DE ARRANQUE V5.7...")
    
    async with httpx.AsyncClient(timeout=20.0) as client:
        # 1. Obter ID do Monitor
        print("🔍 Localizando perfil monitor...")
        r = await client.get(f"https://www.instagram.com/api/v1/users/web_profile_info/?username=monitoramento.discurso", headers=HEADERS_IG)
        if r.status_code != 200:
            print(f"❌ Falha de Autenticação IG: {r.status_code}")
            return
        
        monitor_id = r.json()["data"]["user"]["id"]
        
        # 2. Obter Seguidos
        print(f"📡 Monitor ID: {monitor_id}. Coletando monitorados...")
        r = await client.get(f"https://www.instagram.com/api/v1/friendships/{monitor_id}/following/", headers=HEADERS_IG)
        targets = r.json().get("users", [])[:3] # Pegar os 3 primeiros para o arranque rápido
        
        all_data = []
        for t in targets:
            print(f"👤 monitorado: @{t['username']}. Coletando posts...")
            r_feed = await client.get(f"https://www.instagram.com/api/v1/feed/user/{t['pk']}/", headers=HEADERS_IG)
            posts = r_feed.json().get("items", [])[:1]
            
            for p in posts:
                print(f"💬 Coletando comentários do post {p['code']}...")
                r_c = await client.get(f"https://www.instagram.com/api/v1/media/{p['pk']}/comments/", headers=HEADERS_IG)
                comments = r_c.json().get("comments", [])[:5]
                
                for c in comments:
                    print(f"🧠 Analisando com Groq: {c['text'][:30]}...")
                    res = await analyze(c['text'])
                    all_data.append({
                        "id_externo": str(c["pk"]),
                        "candidato_id": t["username"],
                        "post_id": str(p["pk"]),
                        "autor_username": c["user"]["username"],
                        "texto_bruto": c["text"],
                        "data_publicacao": datetime.fromtimestamp(c["created_at"]).isoformat(),
                        "data_coleta": datetime.now().isoformat(),
                        "is_hate": res.get("is_hate", False) if res else False,
                        "categoria_ia": res.get("categoria", "Neutro") if res else "Erro",
                        "justificativa_ia": res.get("justificativa", "") if res else "",
                        "processado_ia": True if res else False
                    })

        # 3. Upsert Supabase
        if all_data:
            print(f"💾 Enviando {len(all_data)} evidências para o Supabase...")
            r_sb = await client.post(f"{SUPABASE_URL}/rest/v1/comentarios", json=all_data, headers=HEADERS_SB)
            if r_sb.status_code in [200, 201]:
                print("✅ SUCESSO: O Coletor está oficialmente FUNCIONANDO!")
            else:
                print(f"❌ Erro Supabase: {r_sb.text}")

if __name__ == "__main__":
    asyncio.run(kickstart())
