
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.db import db_client

async def purge_youtube():
    if not db_client.client:
        print("Erro: Cliente Supabase não configurado.")
        return

    print("🔥 Iniciando PURGA MÁXIMA de dados do YouTube no Supabase...")
    
    try:
        # Deletar comentários
        print("Apagando comentários do YouTube...")
        res_com = db_client.client.table('comentarios').delete().eq('plataforma', 'youtube').execute()
        print(f"✅ Comentários deletados: {len(res_com.data) if res_com.data else 0}")
        
        # Deletar alertas ativos (se tiverem a coluna plataforma)
        try:
            print("Apagando alertas ativos do YouTube...")
            res_alert = db_client.client.table('alertas_ativos').delete().eq('plataforma', 'youtube').execute()
            print(f"✅ Alertas deletados: {len(res_alert.data) if res_alert.data else 0}")
        except Exception as e:
            print("Nenhuma coluna plataforma em alertas_ativos ou tabela inexistente.")

        # Deletar candidatos
        print("Apagando candidatos do YouTube...")
        res_cand = db_client.client.table('candidatos').delete().eq('plataforma', 'youtube').execute()
        print(f"✅ Candidatos deletados: {len(res_cand.data) if res_cand.data else 0}")

        print("🚀 PURGA CONCLUÍDA! O YouTube foi apagado da existência neste banco de dados.")

    except Exception as e:
        print(f"❌ Erro durante a purga: {e}")

if __name__ == "__main__":
    asyncio.run(purge_youtube())
