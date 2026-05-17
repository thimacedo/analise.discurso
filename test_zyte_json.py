import httpx
import json
import base64

ZYTE_API_KEY = "183c7f26f2da400baf573350b5d55c8c"
API_URL = "https://api.zyte.com/v1/extract"

def test_ig_json_api(target="cironogueira"):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={target}"
    print(f"🚀 Testando API JSON Instagram via Zyte para @{target}...")
    
    payload = {
        "url": url,
        "httpResponseBody": True,
        "customHttpRequestHeaders": [
            {"name": "X-IG-App-ID", "value": "936619743392459"}
        ]
    }
    
    try:
        response = httpx.post(
            API_URL,
            auth=(ZYTE_API_KEY, ""),
            json=payload,
            timeout=60.0
        )
        
        if response.status_code == 200:
            res_data = response.json()
            body_b64 = res_data.get("httpResponseBody")
            if body_b64:
                body_content = base64.b64decode(body_b64).decode('utf-8')
                print(f"✅ Resposta recebida! Tamanho: {len(body_content)}")
                try:
                    data = json.loads(body_content)
                    if "data" in data and "user" in data["data"]:
                        print("💎 SUCESSO! Dados do usuário encontrados.")
                        return True
                    else:
                        print(f"⚠️ Resposta JSON inesperada: {body_content[:500]}")
                except:
                    print(f"❌ Resposta não é JSON: {body_content[:500]}")
            return False
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"💥 Erro: {e}")
        return False

if __name__ == "__main__":
    test_ig_json_api()
