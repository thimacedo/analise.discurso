import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def debug_states():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    r = await httpx.AsyncClient().get(f"{url}/rest/v1/candidatos?select=estado", headers=headers)
    states = [c['estado'] for c in r.json() if c.get('estado')]
    unique_states = set(states)
    print(f"Estados únicos no banco: {unique_states}")
    print(f"Total de registros com estado: {len(states)}")
    print(f"Exemplo de estado: {states[0] if states else 'NENHUM'}")

if __name__ == "__main__":
    asyncio.run(debug_states())
