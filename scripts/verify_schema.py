import os
import sys
import asyncio
from dotenv import load_dotenv
from supabase import create_client, Client

# Força UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

async def verify_schema():
    print("🔍 [VERIFY] Iniciando verificação de schema...")
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ [VERIFY] SUPABASE_URL ou SUPABASE_KEY não encontrados no .env")
        return

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # 1. Verificar se a tabela anuncios existe
    try:
        # Tenta buscar metadados via query vazia ou limit 0
        res = supabase.table('anuncios').select('*').limit(1).execute()
        print("✅ [VERIFY] Tabela 'anuncios' encontrada.")
        
        # 2. Verificar colunas
        if res.data and len(res.data) > 0:
            columns = list(res.data[0].keys())
        else:
            # Se a tabela estiver vazia, o PostgREST não retorna as colunas facilmente no .data
            # Mas podemos tentar inserir um dummy ou usar a API de definições
            print("⚠️ [VERIFY] Tabela encontrada, mas está vazia. Verificando via RPC ou API de metadados...")
            # Fallback: tentar verificar colunas específicas via select filtrado
            try:
                supabase.table('anuncios').select('corpo_anuncio, categoria_ia, confianza_ia, is_hate, processado_ia').limit(0).execute()
                print("✅ [VERIFY] Todas as colunas PASA v16.4 estão presentes.")
                return True
            except Exception as e:
                print(f"❌ [VERIFY] Algumas colunas PASA estão faltando: {e}")
                return False
                
        required_pasa = ['corpo_anuncio', 'categoria_ia', 'confianza_ia', 'is_hate', 'processado_ia']
        missing = [c for c in required_pasa if c not in columns]
        
        if not missing:
            print("✅ [VERIFY] Todas as colunas PASA v16.4 estão presentes.")
            return True
        else:
            print(f"❌ [VERIFY] Colunas ausentes: {missing}")
            return False

    except Exception as e:
        if "Could not find the table" in str(e) or "404" in str(e):
            print("❌ [VERIFY] Tabela 'anuncios' NÃO encontrada.")
        else:
            print(f"❌ [VERIFY] Erro ao verificar tabela: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(verify_schema())
