import httpx
import json

ZYTE_API_KEY = "183c7f26f2da400baf573350b5d55c8c"
API_URL = "https://api.zyte.com/v1/extract"

def test_zyte_social_media_profile(target="cironogueira"):
    url = f"https://www.instagram.com/{target}/"
    print(f"🚀 Testando 'socialMediaProfile' Zyte para @{target}...")
    
    payload = {
        "url": url,
        "socialMediaProfile": True
    }
    
    try:
        response = httpx.post(
            API_URL,
            auth=(ZYTE_API_KEY, ""),
            json=payload,
            timeout=120.0
        )
        
        if response.status_code == 200:
            data = response.json()
            profile = data.get("socialMediaProfile")
            if profile:
                print("💎 SUCESSO! Dados extraídos:")
                print(json.dumps(profile, indent=2, ensure_ascii=False))
                return True
            else:
                print("⚠️ Resposta recebida mas 'socialMediaProfile' está vazio.")
                print(json.dumps(data, indent=2))
                return False
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"💥 Erro: {e}")
        return False

if __name__ == "__main__":
    test_zyte_social_media_profile()
