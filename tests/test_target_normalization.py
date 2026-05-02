import sys
import os
sys.path.append(os.getcwd())

from tools.target_manager import TargetManager
from core.normalizer import target_normalizer

def test_normalization():
    print("🧪 [TEST] Iniciando teste de normalização de alvos...")
    
    # 1. Teste direto do Normalizer
    print("\n--- Teste Direto: TargetNormalizer ---")
    targets = ["Lula", "Bolsonaro", "lulaoficial", "desconhecido_123"]
    normalized = target_normalizer.normalize_list(targets)
    print(f"Original: {targets}")
    print(f"Normalizado: {normalized}")
    
    # 2. Teste integrado via TargetManager
    print("\n--- Teste Integrado: TargetManager ---")
    tm = TargetManager(hours_threshold=0) # Força inclusão de todos
    tm.recently_scraped = set() # Limpa cache de raspagem recente
    
    final_targets = tm.filter_targets(targets)
    print(f"Final para Scraping: {final_targets}")
    
    # Verificações básicas
    assert "lulaoficial" in normalized, "Falha ao normalizar Lula"
    assert "bolsonaromessias" in normalized or "jairmessiasbolsonaro" in normalized, "Falha ao normalizar Bolsonaro"
    print("\n✅ [TEST] Teste de normalização concluído com sucesso!")

if __name__ == "__main__":
    test_normalization()
