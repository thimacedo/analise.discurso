import sys
import os
sys.path.append(os.getcwd())

from tools.target_manager import TargetManager

def test_manager_integration():
    tm = TargetManager()
    
    # Alvos com "Lula" e "Bolsonaro"
    raw_targets = ["Lula", "Bolsonaro", "lulaoficial", "alvo_inexistente_404"]
    print(f"🎯 Testando TargetManager.filter_targets com: {raw_targets}")
    
    filtered = tm.filter_targets(raw_targets)
    print(f"✨ Resultado Filtrado (Normalizado): {filtered}")

    # Verifica se a normalização ocorreu dentro do TargetManager
    # Lula deve virar lulaoficial, Bolsonaro deve virar flaviobolsonaro (ou similar no banco)
    
if __name__ == "__main__":
    test_manager_integration()
