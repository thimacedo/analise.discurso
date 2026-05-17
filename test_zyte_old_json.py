import httpx
import json
import base64

ZYTE_API_KEY = "183c7f26f2da400baf573350b5d55c8c"
API_URL = "https://api.zyte.com/v1/extract"

def test_ig_old_json_api(target="cironogueira"):
    url = f"https://www.instagram.com/{target}/?__a=1&__d=dis"
    print(f"🚀 Testando API Antiga JSON Instagram via Zyte para @{target}...")
    
    payload = {
        "url": url,
        "httpResponseBody": True
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
                    if "graphql" in data or "graphql" in data.get("graphql", {}):
                        print("💎 SUCESSO! Dados graphql encontrados.")
                        return True
                    elif "graphql" in data:
                         print("💎 SUCESSO! Dados graphql encontrados (root).")
                         return True
                    else:
                        print(f"⚠️ Resposta JSON inesperada: {body_content[:500]}")
                        if "login" in body_content.lower():
                            print("⚠️ Detectado redirecionamento para LOGIN no JSON.")
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
    test_ig_old_json_api()
