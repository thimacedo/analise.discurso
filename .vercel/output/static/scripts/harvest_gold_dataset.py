# scripts/harvest_gold_dataset.py
import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.supabase_service import get_supabase_client

def harvest_gold():
    """
    Busca comentários auditados (Gold Standard) e gera um arquivo de treino/contexto para a IA.
    """
    db = get_supabase_client()
    
    print("💎 Coletando Padrão Ouro do banco de dados...")
    
    res = db.table('audit_gold_standards').select('*').execute()
    
    if not res.data:
        print("📭 Nenhum dado de auditoria encontrado. Comece a validar no Dashboard!")
        return

    dataset = []
    for item in res.data:
        dataset.append({
            "text": item['texto_original'],
            "label": item['rotulo_correto'],
            "validator": item['validado_por']
        })

    output_path = PROJECT_ROOT / 'data' / 'classifier_gold_dataset.json'
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Dataset de Ouro colhido: {len(dataset)} exemplos em {output_path}")

if __name__ == "__main__":
    harvest_gold()
