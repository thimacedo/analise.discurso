
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import json
from api.index import summary, trends, pasa_breakdown, geo_uf
from dotenv import load_dotenv

load_dotenv()

def test_api_logic():
    print("🧪 Testando Lógica dos Endpoints da API...")
    
    try:
        print("\n1. Testando /summary...")
        s = summary()
        print(f"✅ OK: {s}")
        
        print("\n2. Testando /trends...")
        t = trends()
        print(f"✅ OK: {len(t)} itens encontrados")
        
        print("\n3. Testando /pasa/breakdown...")
        p = pasa_breakdown()
        print(f"✅ OK: {p}")
        
        print("\n4. Testando /geo/uf...")
        g = geo_uf()
        print(f"✅ OK: {g}")
        
        print("\n✨ Todos os endpoints lógicos estão operacionais.")
        
    except Exception as e:
        print(f"❌ Erro nos testes: {e}")

if __name__ == "__main__":
    test_api_logic()
