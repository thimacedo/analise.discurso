
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from core.db import db_client
import asyncio

async def cleanup():
    print("🧹 Iniciando limpeza de dados ruidosos...")
    
    # 1. Remove itens da fila de coleta que vieram de pesquisas ruidosas
    # Como não temos uma relação direta simples, vamos limpar a fila do dia de hoje
    # para garantir que os alvos errados não sejam raspados.
    res_fila = db_client.client.table('fila_coleta')\
        .delete()\
        .eq('data_agendada', '2026-05-04')\
        .execute()
    print(f"🗑️ Itens removidos da fila de coleta.")

    # 2. Busca IDs de candidatos que possuem ultima_pesquisa_id (os novos)
    res_cand = db_client.client.table('candidatos')\
        .select('username')\
        .filter('ultima_pesquisa_id', 'is', 'not_null')\
        .execute()
    
    usernames = [c['username'] for c in res_cand.data]
    if usernames:
        # Deleta esses candidatos (serão recriados pelo scanner corrigido)
        db_client.client.table('candidatos').delete().in_('username', usernames).execute()
        print(f"🗑️ {len(usernames)} alvos ruidosos removidos.")

    # 3. Limpa a tabela de pesquisas processadas para permitir re-análise dos PDFs
    db_client.client.table('pesquisas_processadas').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
    print(f"🗑️ Histórico de pesquisas resetado para re-processamento.")

if __name__ == "__main__":
    asyncio.run(cleanup())
