
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import os
from dotenv import load_dotenv
from supabase import create_client, Client

async def check_supabase():
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    print(f"🔍 [Check] URL: {url}")
    if not url or not key:
        print("❌ [Check] Credentials missing in .env")
        return

    try:
        supabase: Client = create_client(url, key)
        print("✅ [Check] Supabase client created.")
        
        # Tenta listar as tabelas ou fazer um select simples
        try:
            res = supabase.table('dossies').select('count', count='exact').limit(1).execute()
            print(f"✅ [Check] Tabela 'dossies' acessível. Contagem: {res.count}")
        except Exception as e:
            print(f"❌ [Check] Erro ao acessar tabela 'dossies': {e}")
            
    except Exception as e:
        print(f"❌ [Check] Erro geral: {e}")

if __name__ == "__main__":
    asyncio.run(check_supabase())
