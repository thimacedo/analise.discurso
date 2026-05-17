import re
import json

def analyze_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    print(f"Analisando {file_path} ({len(html)} bytes)...")
    
    # Padrões comuns
    patterns = [
        r'window\._sharedData = (\{.*?\});',
        r'window\.__additionalDataLoaded\(.*?,(\{.*?\})\);',
        r'<script type="application/json" data-dire-initial-data=".*?">(\{.*?\})</script>',
        r'xdt_api__v1__users__web_profile_info.*?(\{.*?\})',
    ]
    
    found = False
    for p in patterns:
        matches = re.findall(p, html, re.DOTALL)
        if matches:
            print(f"✅ Encontrado padrão: {p[:30]}...")
            for m in matches[:1]: # Mostra apenas o primeiro
                print(f"Tamanho do JSON: {len(m)}")
                try:
                    data = json.loads(m)
                    print(f"Chaves no JSON: {list(data.keys())}")
                    found = True
                except:
                    print("❌ Falha ao parsear JSON.")
    
    if not found:
        print("❌ Nenhum padrão JSON conhecido encontrado.")
        if "login" in html.lower():
            print("⚠️ Página contém 'login' - possivelmente redirecionada.")

if __name__ == "__main__":
    analyze_html("debug_ig_profile.html")
