import httpx
import json
import base64

ZYTE_API_KEY = "183c7f26f2da400baf573350b5d55c8c"
API_URL = "https://api.zyte.com/v1/extract"

def test_ig_profile_html(target="cironogueira"):
    url = f"https://www.instagram.com/{target}/"
    print(f"🚀 Testando extração HTML Zyte para @{target}...")
    
    payload = {
        "url": url,
        "browserHtml": True,
        "javascript": True
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
            
            with open("debug_ig_profile.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            if "window._sharedData" in html:
                print("💎 Encontrado window._sharedData!")
            elif "window.__additionalData" in html:
                print("💎 Encontrado window.__additionalData!")
            elif "xdt_api__v1__users__web_profile_info" in html:
                print("💎 Encontrado dados de profile info no HTML!")
            else:
                print("❌ Dados JSON não encontrados no HTML.")
                if "login" in html.lower():
                    print("⚠️ Detectado redirecionamento para LOGIN.")
            
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"💥 Erro: {e}")
        return False

if __name__ == "__main__":
    test_ig_profile_html()
