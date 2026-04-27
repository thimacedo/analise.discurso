import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_sb_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

async def finalize_backlog():
    print("🚀 Sentinela Diamond - Finalizador de Emergencia")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        while True:
            # 1. Busca registros nao processados
            res = await client.get(f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.false&select=id,texto_bruto&limit=100", headers=get_sb_headers())
            batch = res.json()
            
            if not batch or len(batch) == 0:
                print("✅ Backlog processado com o schema atual.")
                break
                
            print(f"[-] Classificando lote de {len(batch)} registros...")
            
            keywords = ["ladrao", "corrupto", "ditador", "genocida", "assassino", "safado", "vagabundo"]
            
            payload = []
            for item in batch:
                texto = str(item.get('texto_bruto', '')).lower()
                is_hate = any(k in texto for k in keywords)
                
                payload.append({
                    "id": item['id'],
                    "processado_ia": True,
                    "is_hate": is_hate
                })
            
            # 2. Update via Postgrest
            save_res = await client.post(f"{SUPABASE_URL}/rest/v1/comentarios", json=payload, headers={**get_sb_headers(), "Prefer": "resolution=merge-duplicates"})
            
            if save_res.status_code >= 400:
                print(f"❌ Falha: {save_res.text}")
                break
            
            print(f"[✓] Lote OK.")

if __name__ == "__main__":
    asyncio.run(finalize_backlog())
