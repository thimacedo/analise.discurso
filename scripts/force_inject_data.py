import os
import json
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def inject():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }

    if not os.path.exists("raw_data.json"):
        print("❌ Arquivo raw_data.json não encontrado.")
        return

    # Tenta ler com detecção de codificação ou UTF-16 que é o padrão do redirecionamento do PowerShell
    try:
        with open("raw_data.json", "r", encoding="utf-16") as f:
            raw_content = f.read()
    except:
        with open("raw_data.json", "r", encoding="utf-8", errors='ignore') as f:
            raw_content = f.read()

    try:
        json_start = raw_content.find("[")
        if json_start == -1:
            print("❌ Não foi possível localizar o início do JSON no arquivo.")
            return
        data = json.loads(raw_content[json_start:])
    except Exception as e:
        print(f"❌ Erro ao ler JSON: {e}")
        return

    comentarios_para_salvar = []
    now = datetime.now().isoformat()
    investigator_id = "66f853ed-c42b-43d4-bcc3-23f05b2c44e9"

    for post in data:
        username = post.get("ownerUsername", "unknown")
        shortcode = post.get("shortCode", "unknown")
        
        # Garante que o candidato existe (Handshake)
        httpx.post(f"{url}/rest/v1/candidatos", json={"username": username}, headers=headers)

        comments = post.get("latestComments", [])
        for c in comments:
            comentarios_para_salvar.append({
                "id_externo": str(c.get("id")),
                "candidato_id": username,
                "post_id": shortcode,
                "autor_username": str(c.get("ownerUsername")),
                "texto_bruto": str(c.get("text")),
                "data_coleta": now,
                "data_publicacao": c.get("timestamp"),
                "likes": c.get("likesCount", 0),
                "user_id": investigator_id
            })

    if comentarios_para_salvar:
        print(f"🚀 Injetando {len(comentarios_para_salvar)} comentários no Supabase...")
        # Quebrar em lotes de 50 para evitar limites de payload
        for i in range(0, len(comentarios_para_salvar), 50):
            batch = comentarios_para_salvar[i:i+50]
            r = httpx.post(f"{url}/rest/v1/comentarios", json=batch, headers=headers)
            if r.status_code in [200, 201]:
                print(f"   ✅ Lote {i//50 + 1} sincronizado.")
            else:
                print(f"   ❌ Erro Lote {i//50 + 1}: {r.text}")
    else:
        print("⚠️ Nenhum comentário válido encontrado para injeção.")

if __name__ == "__main__":
    inject()
