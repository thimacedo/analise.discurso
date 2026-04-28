import httpx
import os
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

async def debug():
    headers = {
        'x-rapidapi-key': os.getenv('RAPIDAPI_KEY'),
        'x-rapidapi-host': 'instagram-scraper-20251.p.rapidapi.com'
    }
    async with httpx.AsyncClient() as client:
        # Testando endpoint de info para ver estrutura
        url = 'https://instagram-scraper-20251.p.rapidapi.com/info?username=lulaoficial'
        print(f'[-] Testando API: {url}')
        r = await client.get(url, headers=headers)
        print(f'Status: {r.status_code}')
        if r.status_code == 200:
            data = r.json()
            print('Estrutura de chaves:', list(data.keys()))
            # Se tiver 'data', ver sub-chaves
            if 'data' in data:
                print('Sub-chaves de data:', list(data['data'].keys()) if isinstance(data['data'], dict) else 'Lista')
        else:
            print(f'Erro: {r.text}')

if __name__ == '__main__':
    asyncio.run(debug())
