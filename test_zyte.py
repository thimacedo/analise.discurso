import httpx
import json

ZYTE_API_KEY = "183c7f26f2da400baf573350b5d55c8c"
API_URL = "https://api.zyte.com/v1/extract"

def test_zyte_connection():
    print(f"🚀 Testando conexão Zyte API com a chave: {ZYTE_API_KEY[:4]}...")
    
    payload = {
        "url": "https://toscrape.com",
        "httpResponseBody": True
    }
    
    try:
        response = httpx.post(
            API_URL,
            auth=(ZYTE_API_KEY, ""),
            json=payload,
            timeout=30.0
        )
        
        if response.status_code == 200:
            print("✅ Sucesso! Zyte API respondeu corretamente.")
            data = response.json()
            print(f"📦 Status do Job: {data.get('status', 'N/A')}")
            return True
        else:
            print(f"❌ Erro na API Zyte: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Erro na requisição: {e}")
        return False

if __name__ == "__main__":
    test_zyte_connection()
