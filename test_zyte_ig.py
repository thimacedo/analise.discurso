import httpx
import json

ZYTE_API_KEY = "183c7f26f2da400baf573350b5d55c8c"
API_URL = "https://api.zyte.com/v1/extract"

def test_instagram_zyte():
    target = "cironogueira"
    url = f"https://www.instagram.com/{target}/"
    print(f"🚀 Testando extração Zyte para @{target}...")
    
    payload = {
        "url": url,
        "browserHtml": True
    }
    
    try:
        response = httpx.post(
            API_URL,
            auth=(ZYTE_API_KEY, ""),
            json=payload,
            timeout=60.0
        )
        
        if response.status_code == 200:
            data = response.json()
            html = data.get('browserHtml', '')
            print(f"✅ Sucesso! Recebidos {len(html)} bytes de HTML.")
            if "login" in html.lower() and "instagram" in html.lower():
                 print("⚠️ Detectado redirecionamento para login.")
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"💥 Erro: {e}")
        return False

if __name__ == "__main__":
    test_instagram_zyte()
