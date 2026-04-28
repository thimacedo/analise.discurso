import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

HEADERS_SB = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

async def fetch_and_inject():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Lista datasets recentes
        r_list = await client.get(f"https://api.apify.com/v2/datasets?token={APIFY_TOKEN}&unnamed=true&desc=true&limit=20")
        datasets = r_list.json()["data"]["items"]
        
        print(f"🕵️ Encontrados {len(datasets)} datasets. Iniciando extração profunda...")
        
        for ds in datasets:
            if ds["itemCount"] == 0: continue
            
            # 2. Busca itens do dataset
            r_items = await client.get(f"https://api.apify.com/v2/datasets/{ds['id']}/items?token={APIFY_TOKEN}")
            items = r_items.json()
            
            payload = []
            for item in items:
                # Normalização para a tabela 'comentarios'
                texto = item.get("text", item.get("caption", item.get("body", "")))
                if not texto: continue
                
                payload.append({
                    "id_externo": str(item.get("id", item.get("id_externo", ds["id"]))),
                    "candidato_id": "coleta_automatica", # Marcador genérico se não houver ID
                    "texto_bruto": texto,
                    "autor_username": item.get("ownerUsername", item.get("username", "anonimo")),
                    "data_publicacao": item.get("timestamp", ds["createdAt"]),
                    "processado_ia": False
                })
            
            if payload:
                print(f"   📥 Injetando {len(payload)} itens do dataset {ds['id']}...")
                await client.post(f"{SUPABASE_URL}/rest/v1/comentarios", json=payload, headers=HEADERS_SB)

if __name__ == "__main__":
    asyncio.run(fetch_and_inject())
