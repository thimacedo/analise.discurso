
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY") # Deve ser a service_role key para DDL
supabase = create_client(url, key)

with open('scripts/create_anuncios_table.sql', 'r', encoding='utf-8') as f:
    sql = f.read()

# O client de Python do Supabase não tem um método 'sql' direto exposto facilmente para DDL bruto via PostgREST
# Normalmente se usa uma RPC ou a dashboard. 
# Vou tentar executar via um pequeno script usando psycopg2 se disponível, ou assumir que o usuário aplicará se falhar.
# No entanto, posso tentar criar via a própria API de tabelas se for o caso, mas o SQL é mais complexo (RLS, etc).
print("--- SQL A SER APLICADO ---")
print(sql)
print("--------------------------")
