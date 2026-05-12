
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.supabase_service import get_supabase_client

async def main():
    if not db_client.client:
        print("Erro: Cliente Supabase não configurado.")
        return

    print("🔍 Buscando candidatos (Presidente/Governador) no Supabase...")
    try:
        # Busca candidatos
        res = db_client.client.table('candidatos').select('username, cargo, partido, comentarios_totais_count, comentarios_odio_count').execute()
        candidatos = res.data
        
        print(f"Total de candidatos no banco: {len(candidatos)}")
        
        high_priority = []
        
        for c in candidatos:
            cargo = str(c.get('cargo', '')).lower()
            comentarios = c.get('comentarios_totais_count')
            
            if 'presidente' in cargo or 'governador' in cargo:
                if comentarios is None or comentarios == 0:
                    high_priority.append(c)

        print("\n🚨 PRIORIDADE ALTA (Presidentes/Governadores com 0 raspagem no Banco):")
        for c in high_priority:
            print(f"- @{c['username']} ({c.get('cargo')} - {c.get('partido')})")
            
        if not high_priority:
            print("- Nenhum encontrado. Todos os caciques do banco já foram raspados.")

    except Exception as e:
        print(f"Erro ao consultar DB: {e}")

if __name__ == "__main__":
    asyncio.run(main())
