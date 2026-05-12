
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import sys
import os
# Adiciona o diretório raiz ao path para importar core
sys.path.append(os.getcwd())

from core.normalizer import target_normalizer

def test_normalization():
    test_cases = ["Lula", "Bolsonaro", "Ciro Gomes", "lulaoficial", "desconhecido_perfil_123"]
    print(f"🧪 Testando normalização para: {test_cases}")
    
    results = target_normalizer.normalize_list(test_cases)
    print(f"✨ Resultados: {results}")

    # Verifica se os conhecidos foram traduzidos (assumindo que estão no banco)
    # Nota: Este teste depende dos dados reais do Supabase
    
if __name__ == "__main__":
    test_normalization()
