"""
PASA v31.1 - Mass Classify: Processamento com Schema Real
"""
from core.supabase_service import get_supabase_client
from app.ai.classifier_engine import classify_batch, VALID_CATEGORIAS

# Inicializa o cliente Supabase
db = get_supabase_client()

BATCH_SIZE = 30 

def process_mass_classification():
    offset = 0
    total_classified = 0
    
    while True:
        # Busca comentários onde processado_ia é falso ou nulo
        pending = db.table('comentarios')\
            .select('id, texto_bruto')\
            .neq('processado_ia', True)\
            .limit(BATCH_SIZE)\
            .offset(offset)\
            .execute()

        if not pending.data:
            print(f"[MassClassify] Fim do processamento. Total classificado: {total_classified}")
            break

        batch = pending.data
        # Ajusta para o formato que a engine espera
        formatted_batch = [{'id': c['id'], 'texto': c['texto_bruto']} for c in batch]
        print(f"[MassClassify] Processando lote de {len(formatted_batch)} comentários...")

        classifications = classify_batch(formatted_batch)

        if not classifications:
            offset += BATCH_SIZE
            continue

        for c in classifications:
            if not c.get('id'): continue
            
            is_hate = c.get('rotulo') == 'hate'
            categoria = c.get('categoria_ia', 'Neutro')
            direcao = c.get('direcao_odio') if is_hate else None
            confianca = float(c.get('confianca_ia', 0.5))
            
            if categoria not in VALID_CATEGORIAS:
                categoria = "Neutro"

            # Mapeamento exato para o schema do Supabase
            db.table('comentarios').update({
                'is_hate': is_hate,
                'processado_ia': True,
                'categoria_ia': categoria,
                'direcao_odio': direcao,
                'confianca_ia': confianca
            }).eq('id', c['id']).execute()

        total_classified += len(classifications)
        offset += BATCH_SIZE

if __name__ == "__main__":
    process_mass_classification()
