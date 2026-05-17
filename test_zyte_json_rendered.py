import httpx
import json
import base64

ZYTE_API_KEY = "183c7f26f2da400baf573350b5d55c8c"
API_URL = "https://api.zyte.com/v1/extract"

def test_ig_json_rendered(target="cironogueira"):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={target}"
    print(f"🚀 Testando API JSON Renderizada Instagram via Zyte para @{target}...")
    
    payload = {
        "url": url,
        "browserHtml": True,
        "customHttpRequestHeaders": [
            {"name": "X-IG-App-ID", "value": "936619743392459"}
        ]
    }
    
    try:
        response = httpx.post(
            API_URL,
            auth=(ZYTE_API_KEY, ""),
            json=payload,
            timeout=120.0
        )
        
        if response.status_code == 200:
            res_data = response.json()
            html = res_data.get("browserHtml", "")
            print(f"✅ Resposta recebida! Tamanho: {len(html)}")
            
            # Tenta extrair o JSON do HTML (se o navegador renderizar o JSON como texto)
            if "{" in html and "}" in html:
                try:
                    # Muitas vezes o JSON aparece dentro de um <pre> ou apenas no body
                    import re
                    json_match = re.search(r'(\{.*\})', html, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        data = json.loads(json_str)
                        if "data" in data:
                            print("💎 SUCESSO! Dados encontrados no HTML renderizado.")
                            return True
                except:
                    pass
            
            print(f"⚠️ Conteúdo renderizado: {html[:1000]}")
            return False
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"💥 Erro: {e}")
        return False

if __name__ == "__main__":
    test_ig_json_rendered()
