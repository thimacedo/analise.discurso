"""
PASA v25 - Fetch Pending: Processamento em Lote Real
Substitui o stub anterior, integrando a API de IA para esvaziar a fila de pendências.
"""
from core.supabase_service import supabase
from app.ai.classifier_engine import classify_batch

BATCH_SIZE = 20 # Processa 20 comentários por vez para otimizar tokens/latência

def process_pending_comments():
    print(f"[FetchPending] Buscando até {BATCH_SIZE} comentários pendentes...")
    
    # 1. Busca lote de comentários não classificados
    # Adaptado para o schema real: texto_bruto e processado_ia
    try:
        pending = supabase.table('comentarios')\
            .select('id, texto_bruto')\
            .eq('processado_ia', False)\
            .limit(BATCH_SIZE)\
            .execute()
    except Exception as e:
        print(f"[FetchPending] Erro ao buscar comentários: {e}")
        return

    if not pending.data:
        print("[FetchPending] Nenhum comentário pendente. Sistema limpo.")
        return

    batch = pending.data
    print(f"[FetchPending] Processando lote de {len(batch)} comentários...")

    # 2. Classifica usando a API real em lote
    classifications = classify_batch(batch)

    if not classifications:
        print("[FetchPending] Falha na classificação do lote. Abortando.")
        return

    # 3. Atualiza o banco em massa
    success_count = 0
    for classification in classifications:
        comment_id = classification.get('id')
        rotulo = classification.get('rotulo')
        
        if not comment_id or not rotulo:
            continue

        is_hate = rotulo == 'hate'
        
        try:
            supabase.table('comentarios').update({
                'is_hate': is_hate,
                'processado_ia': True,
                'categoria_ia': 'ODIO' if is_hate else 'NEUTRO',
                'confianca_ia': 0.95 # Confiança base do lote
            }).eq('id', comment_id).execute()
            success_count += 1
        except Exception as e:
            print(f"[FetchPending] Erro ao atualizar comentário {comment_id}: {e}")

    print(f"[FetchPending] Lote de {success_count} comentários classificado e salvo.")

if __name__ == "__main__":
    process_pending_comments()
