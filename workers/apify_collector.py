import httpx
import os
import asyncio
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_sb_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}

async def run_apify_scraper(usernames):
    print(f"?? [APIFY] Iniciando raspagem para: {', '.join(usernames)}")
    run_url = f"https://api.apify.com/v2/acts/apify~instagram-comment-scraper/runs?token={APIFY_TOKEN}"
    
    # Configuração do Actor Apify
    payload = {
        "directUrls": [f"https://www.instagram.com/{u}/" for u in usernames],
        "resultsLimit": 10,
        "commentsLimit": 20
    }

    async with httpx.AsyncClient(timeout=300.0) as client:
        res = await client.post(run_url, json=payload)
        if res.status_code not in [200, 201]:
            print(f"? Erro ao iniciar Apify: {res.text}")
            return None
        
        run_data = res.json().get('data', {})
        run_id = run_data.get('id')
        dataset_id = run_data.get('defaultDatasetId')
        
        print(f"? Run ID: {run_id}. Aguardando conclusão...")
        
        # Polling simples
        for _ in range(30): # Máximo 5 min
            status_res = await client.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}")
            status = status_res.json().get('data', {}).get('status')
            if status == 'SUCCEEDED':
                print("? Raspagem concluída!")
                items_res = await client.get(f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={APIFY_TOKEN}")
                return items_res.json()
            if status in ['FAILED', 'ABORTED']:
                print(f"? Run falhou com status: {status}")
                return None
            await asyncio.sleep(10)
    return None

async def salvar_comentarios(items, alvos_map):
    if not items: return
    
    payload = []
    for item in items:
        username_alvo = item.get('ownerUsername') # Username do dono do post
        if not username_alvo: continue
        
        c_id = alvos_map.get(username_alvo)
        if not c_id: continue

        payload.append({
            "candidato_id": c_id,
            "texto_bruto": item.get('text', ''),
            "autor_username": item.get('ownerUsername', 'anonimo'),
            "fonte_coleta": "Apify/Instagram",
            "processado_ia": False
        })

    if payload:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{SUPABASE_URL}/rest/v1/comentarios", headers=get_sb_headers(), json=payload)
            print(f"?? {len(payload)} comentários profissionais persistidos. Status: {r.status_code}")

async def main():
    # Busca alvos ativos
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/candidatos?status_monitoramento=eq.Ativo&select=id,username&limit=3", headers=get_sb_headers())
        alvos = r.json()
    
    if not alvos:
        print("Fila de alvos vazia.")
        return

    alvos_map = {a['username']: a['id'] for a in alvos}
    items = await run_apify_scraper(list(alvos_map.keys()))
    await salvar_comentarios(items, alvos_map)

if __name__ == '__main__':
    asyncio.run(main())
