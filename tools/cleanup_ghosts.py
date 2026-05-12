import asyncio
import os
import sys

# Adiciona o root do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.supabase_service import get_supabase_client

# Configura a codificação UTF-8 para a saída padrão
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

async def cleanup_ghosts():
    print("Iniciando faxina Diamond de usuários fantasmas...")
    
    # Lista de termos técnicos e links de sistema para limpar
    ghost_terms = [
        'about', 'help', 'privacy', 'terms', 'locations', 
        'popular', 'lite', 'careers', 'instagram', 'meta', 
        'blog', 'threads', 'facebook'
    ]
    
    try:
        # 1. Deleta perfis que contêm caracteres de query string (links de sistema)
        res1 = db_client.client.table('comentarios').delete().ilike('autor_username', '%?%').execute()
        print(f"✅ Removidos registros de links de sistema (?).")
        
        # 2. Deleta perfis da lista de termos técnicos
        res2 = db_client.client.table('comentarios').delete().in_('autor_username', ghost_terms).execute()
        print(f"✅ Removidos registros de termos técnicos: {ghost_terms}")
        
        print("\n✨ Corpus purificado com sucesso! Próximo passo: Ciência de verdade.")
        
    except Exception as e:
        print(f"❌ Erro durante a limpeza: {e}")

if __name__ == "__main__":
    asyncio.run(cleanup_ghosts())
