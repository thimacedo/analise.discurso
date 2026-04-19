import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def sanitize():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    async with httpx.AsyncClient() as client:
        # Busca itens com erro de codificação provável
        r = await client.get(f"{url}/rest/v1/comentarios?texto_bruto=like.*ÔÇ*&limit=100", headers=headers)
        data = r.json()
        
        print(f"🧹 Sanitizando {len(data)} registros com erro de encoding...")
        for item in data:
            raw = item['texto_bruto']
            # Tenta converter mojibake (Windows-1252 -> UTF-8)
            try:
                fixed = raw.encode('windows-1252').decode('utf-8')
            except:
                fixed = raw.replace('ÔÇÖ', "'").replace('ÔØñ', '❤').replace('´©Å', '')
            
            await client.patch(
                f"{url}/rest/v1/comentarios?id=eq.{item['id']}", 
                json={"texto_bruto": fixed}, 
                headers=headers
            )
        print("✅ Sanitização concluída.")

if __name__ == "__main__":
    asyncio.run(sanitize())
