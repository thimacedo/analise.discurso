import os
import json
import subprocess
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def run_extraction(target):
    print(f"\n🔥 [ELITE] Iniciando extração massiva: @{target}")
    run_input = {
        "resultsType": "posts",
        "directUrls": [f"https://www.instagram.com/{target}/"],
        "resultsLimit": 5,
        "proxy": {"useApifyProxy": True}
    }
    
    input_file = f"temp_input_{target}.json"
    output_file = f"data/raw_{target}.json"
    
    with open(input_file, "w") as f:
        json.dump(run_input, f)
    
    try:
        # Chama Apify CLI
        subprocess.run(f"apify call apify/instagram-scraper --input-file {input_file} --output-dataset > {output_file}", shell=True, check=True)
        return output_file
    except Exception as e:
        print(f"   ❌ Falha na extração de @{target}: {e}")
        return None
    finally:
        if os.path.exists(input_file): os.remove(input_file)

def inject_to_supabase(target, file_path):
    if not os.path.exists(file_path): return

    try:
        # Lê o arquivo (tratando codificação do PowerShell)
        try:
            with open(file_path, "r", encoding="utf-16") as f:
                content = f.read()
        except:
            with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
                content = f.read()

        json_start = content.find("[")
        if json_start == -1: return
        data = json.loads(content[json_start:])
    except Exception as e:
        print(f"   ❌ Erro ao ler JSON de @{target}: {e}")
        return

    comentarios = []
    now = datetime.now().isoformat()
    
    # Handshake Candidato
    httpx.post(f"{SUPABASE_URL}/rest/v1/candidatos", json={"username": target}, headers=HEADERS)

    for post in data:
        shortcode = post.get("shortCode", "unknown")
        for c in post.get("latestComments", []):
            comentarios.append({
                "id_externo": str(c.get("id")),
                "candidato_id": target,
                "post_id": shortcode,
                "autor_username": str(c.get("ownerUsername")),
                "texto_bruto": str(c.get("text")),
                "data_coleta": now,
                "data_publicacao": c.get("timestamp"),
                "likes": c.get("likesCount", 0),
                "user_id": "66f853ed-c42b-43d4-bcc3-23f05b2c44e9"
            })

    if comentarios:
        print(f"   🚀 Injetando {len(comentarios)} evidências de @{target}...")
        for i in range(0, len(comentarios), 50):
            batch = comentarios[i:i+50]
            httpx.post(f"{SUPABASE_URL}/rest/v1/comentarios", json=batch, headers=HEADERS)
        print(f"   ✅ Sincronização concluída.")

def main():
    if not os.path.exists("data/priority_queue.json"):
        print("❌ Fila não encontrada.")
        return

    with open("data/priority_queue.json", "r") as f:
        queue = json.load(f)

    print(f"🕵️ ORQUESTRADOR DE ELITE v7.1 - monitorados: {len(queue)}")
    
    for target in queue:
        raw_file = run_extraction(target)
        if raw_file:
            inject_to_supabase(target, raw_file)
            # if os.path.exists(raw_file): os.remove(raw_file)

if __name__ == "__main__":
    main()
