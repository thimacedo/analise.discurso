import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def reset():
    headers = {
        "apikey": os.getenv("SUPABASE_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
    }
    url = os.getenv("SUPABASE_URL")
    
    async with httpx.AsyncClient() as client:
        # Busca os 10 mais recentes
        r = await client.get(
            f"{url}/rest/v1/comentarios?select=id_externo&limit=10&order=data_coleta.desc", 
            headers=headers
        )
        data = r.json()
        ids = [i['id_externo'] for i in data]
        
        print(f"🔄 Resetando {len(ids)} itens para re-processamento v6.3...")
        for idx in ids:
            await client.patch(
                f"{url}/rest/v1/comentarios?id_externo=eq.{idx}", 
                json={"processado_ia": False}, 
                headers=headers
            )
        print("✅ Reset concluído.")

if __name__ == "__main__":
    asyncio.run(reset())
