import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def get_counts():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Erro: Credenciais Supabase não encontradas no .env")
        return

    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Prefer": "count=exact"
    }
    
    async with httpx.AsyncClient() as client:
        # Contagem de Candidatos
        resp_cand = await client.get(f"{url}/rest/v1/candidatos?select=id", headers=headers)
        total_cand = resp_cand.headers.get("Content-Range", "0-0/0").split("/")[-1]
        
        # Contagem de Candidatos Ativos
        # Tentamos Ativo (case sensitive as seen in sample)
        resp_active = await client.get(f"{url}/rest/v1/candidatos?status_monitoramento=eq.Ativo&select=id", headers=headers)
        active_cand = resp_active.headers.get("Content-Range", "0-0/0").split("/")[-1]
        
        # Contagem de Comentários
        resp_com = await client.get(f"{url}/rest/v1/comentarios?select=id", headers=headers)
        total_com = resp_com.headers.get("Content-Range", "0-0/0").split("/")[-1]
        
        # Contagem de Comentários Não Processados (NULL ou False)
        resp_unproc = await client.get(f"{url}/rest/v1/comentarios?processado_ia=is.null&select=id", headers=headers)
        unproc_null = int(resp_unproc.headers.get("Content-Range", "0-0/0").split("/")[-1])
        
        resp_unproc_f = await client.get(f"{url}/rest/v1/comentarios?processado_ia=eq.false&select=id", headers=headers)
        unproc_false = int(resp_unproc_f.headers.get("Content-Range", "0-0/0").split("/")[-1])
        
        total_unproc = unproc_null + unproc_false

        # Contagem de Comentários com Ódio
        resp_hate = await client.get(f"{url}/rest/v1/comentarios?is_hate=eq.true&select=id", headers=headers)
        hate_com = resp_hate.headers.get("Content-Range", "0-0/0").split("/")[-1]

        print(f"📊 RELATÓRIO DE STATUS - SENTINELA")
        print(f"----------------------------------")
        print(f"Candidatos Totais: {total_cand}")
        print(f"Candidatos Ativos: {active_cand}")
        print(f"Comentários Totais: {total_com}")
        print(f"Comentários Pendentes (IA): {total_unproc} (Null: {unproc_null}, False: {unproc_false})")
        print(f"Comentários com Ódio: {hate_com}")

if __name__ == "__main__":
    asyncio.run(get_counts())
