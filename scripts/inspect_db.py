import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

url = f"{SUPABASE_URL}/rest/v1/comentarios?select=processado_ia,is_hate,categoria_ia&limit=100"
resp = httpx.get(url, headers=HEADERS)
if resp.status_code == 200:
    data = resp.json()
    print(f"Total amostra: {len(data)}")
    unprocessed = [d for d in data if not d.get('processado_ia')]
    hate = [d for d in data if d.get('is_hate')]
    print(f"Não processados: {len(unprocessed)}")
    print(f"Com ódio: {len(hate)}")
    
    categories = {}
    for d in data:
        cat = d.get('categoria_ia', 'NULL')
        categories[cat] = categories.get(cat, 0) + 1
    print(f"Categorias: {categories}")
else:
    print(f"Erro: {resp.status_code} - {resp.text}")
