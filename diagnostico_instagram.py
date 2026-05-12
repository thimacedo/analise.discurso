# diagnostico_instagram.py
import requests
import sys
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def diagnosticar_instagram(username: str = "instagram"):
    """Testa o endpoint atual e retorna o diagnóstico bruto."""
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    
    # Headers simulando um navegador real
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }

    print(f"🚀 Disparando requisição de diagnóstico para: {url}\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        print(f"📊 STATUS CODE: {response.status_code}")
        print(f"📏 TAMANHO DA RESPOSTA: {len(response.text)} caracteres")
        print("-" * 50)
        
        # Tenta parsear como JSON para ver se tivemos sorte
        try:
            data = response.json()
            print("✅ A RESPOSTA É JSON VÁLIDO!")
            print("Primeiros 500 caracteres do JSON:")
            print(json.dumps(data, indent=2)[:500])
        except json.JSONDecodeError:
            print("❌ A RESPOSTA NÃO É JSON. A Meta provavelmente retornou HTML (Página de Login/Bloqueio).")
            print("Primeiros 800 caracteres do HTML retornado:")
            print(response.text[:800])
            
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")

if __name__ == "__main__":
    # Usando o perfil oficial do Instagram como cobaia, pois é público e estável
    diagnosticar_instagram("instagram")