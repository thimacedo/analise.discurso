
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# No Supabase Python client, we can't easily list tables via API
# But we can try to query the information_schema via RPC if enabled, 
# or just try to select from 'anuncios' to see if it fails.

try:
    res = supabase.table('anuncios').select('*').limit(1).execute()
    print("✅ Tabela 'anuncios' existe.")
    print(f"Colunas: {res.data[0].keys() if res.data else 'Vazia, mas existe.'}")
except Exception as e:
    print(f"❌ Tabela 'anuncios' NÃO existe ou erro: {e}")

# Try candidates to see if columns are there
try:
    res = supabase.table('candidatos').select('*').limit(1).execute()
    print("✅ Tabela 'candidatos' existe.")
    print(f"Colunas: {res.data[0].keys() if res.data else 'Vazia.'}")
except Exception as e:
    print(f"❌ Erro em candidatos: {e}")
