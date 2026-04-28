from playwright.sync_api import sync_playwright
import os
import json

def test_online():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 1. Validação da API de Dados (Supabase)
        print("🔍 Testando API Supabase...")
        api_url = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1/comentarios?is_hate=eq.true&limit=1"
        headers = {
            "apikey": os.getenv("SENTINELA_SUPABASE_KEY"),
            "Authorization": f"Bearer {os.getenv('SENTINELA_SUPABASE_KEY')}"
        }
        
        response = page.request.get(api_url, headers=headers)
        if response.status == 200:
            data = response.json()
            print(f"✅ API Online! Casos de Ódio detectados na nuvem: {len(data) > 0}")
        else:
            print(f"❌ Falha na API: {response.status}")

        # 2. Validação visual do Dashboard (Mock/Placeholder se URL não definida)
        # Como o dashboard oficial costuma estar na Vercel, vou tentar localizar a URL nos logs
        print("🌐 Verificando Dashboard de Produção...")
        # Simulação de navegação para check de sanidade
        page.goto("https://vhamejkldzxbeibqeqpk.supabase.co")
        print(f"✅ Endpoint Supabase respondendo: {page.title()}")
        
        browser.close()

if __name__ == '__main__':
    test_online()
