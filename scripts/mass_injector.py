import os
import json
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

async def inject_files():
    data_dir = os.path.join(os.getcwd(), "data")
    files = [f for f in os.listdir(data_dir) if f.startswith("raw_") and f.endswith(".json")]
    
    print(f"🚀 Detectados {len(files)} arquivos para injeção.")
    
    async with httpx.AsyncClient() as client:
        for file in files:
            try:
                with open(os.path.join(data_dir, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    if not content: continue
                    
                    # Tenta encontrar o início do array JSON
                    start_idx = content.find("[")
                    end_idx = content.rfind("]")
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        json_str = content[start_idx:end_idx+1]
                        raw_data = json.loads(json_str)
                    else:
                        print(f"   ⚠️ Falha ao encontrar JSON em {file}")
                        continue
                
                candidato_id = file.replace("raw_", "").replace(".json", "")
                payload = []
                for item in raw_data:
                    payload.append({
                        "id_externo": str(item.get("id", item.get("id_externo"))),
                        "candidato_id": candidato_id,
                        "texto_bruto": item.get("text", item.get("texto_bruto")),
                        "autor_username": item.get("ownerUsername", item.get("autor_username")),
                        "data_publicacao": item.get("timestamp", item.get("data_publicacao")),
                        "processado_ia": False
                    })
                
                if payload:
                    print(f"   📥 Injetando {len(payload)} itens de @{candidato_id}...")
                    r = await client.post(f"{SUPABASE_URL}/rest/v1/comentarios", json=payload, headers=HEADERS)
                    if r.status_code not in [201, 204]:
                        print(f"   ⚠️ Erro @{candidato_id}: {r.status_code} - {r.text}")
            except Exception as e:
                print(f"   ❌ Erro no arquivo {file}: {e}")

if __name__ == "__main__":
    asyncio.run(inject_files())
