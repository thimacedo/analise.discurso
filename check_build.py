import os
import sys

def check_structure():
    print("🛡️ Iniciando Vigilante de Build Sentinela...")
    
    required_files = ["index.html", "analise.html", "metodo.html", "vercel.json", "api/index.py"]
    missing = []
    
    for f in required_files:
        if not os.path.exists(f):
            missing.append(f)
            
    if missing:
        print(f"❌ ERRO: Arquivos críticos ausentes: {missing}")
        sys.exit(1)
    
    print("✅ Estrutura validada. Pronto para o deploy.")

if __name__ == "__main__":
    check_structure()
