"""
PASA v36 - Threat Profiler: Calcula a Densidade de Ódio e atualiza o perfil dos alvos
"""
import sys
import os

# Adiciona a raiz do projeto ao path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.supabase_service import get_supabase_client

def calculate_hate_density():
    db = get_supabase_client()
    
    # 1. Busca todos os candidatos monitorados
    candidates = db.table('candidatos').select('id, username, comentarios_odio_count, comentarios_totais_count').execute()
    
    if not candidates.data:
        print("[ThreatProfiler] Nenhum candidato encontrado.")
        return

    print(f"[ThreatProfiler] Calculando densidade para {len(candidates.data)} alvos...")

    for cand in candidates.data:
        cand_id = cand['id']
        username = cand['username']
        
        # 2. Conta comentários totais e de ódio diretamente da tabela de comentários (Fonte da Verdade)
        # Nota: Usamos candidato_id que mapeia para o username na tabela de comentários conforme lógica do orquestrador
        try:
            total_comments = db.table('comentarios').select('id', count='exact').eq('candidato_id', username).execute()
            hate_comments = db.table('comentarios').select('id', count='exact').eq('candidato_id', username).eq('is_hate', True).execute()

            total = total_comments.count if total_comments.count is not None else 0
            hate = hate_comments.count if hate_comments.count is not None else 0

            if total == 0:
                density = 0
            else:
                density = round((hate / total) * 100, 2)
            
            # 3. Atualiza a tabela de candidatos com as novas métricas
            db.table('candidatos').update({
                'comentarios_totais_count': total,
                'comentarios_odio_count': hate,
                'nota_relevancia': density # Usamos o campo nota_relevancia como Densidade de Ameaça
            }).eq('id', cand_id).execute()

            print(f"[ThreatProfiler] @{username} | Total: {total} | Ódio: {hate} | Densidade: {density}%")
        except Exception as e:
            print(f"[ThreatProfiler] Erro ao processar @{username}: {e}")

    print("[ThreatProfiler] Perfil de ameaças atualizado com sucesso.")

if __name__ == "__main__":
    calculate_hate_density()
