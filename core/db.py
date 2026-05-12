# core/db.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# No backend Python, usamos a SERVICE_ROLE_KEY, que tem permissão de administrador.
# A ANON_KEY é só para o frontend. Nunca exponha a SERVICE_ROLE_KEY no frontend!
URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not URL or not KEY:
    raise ValueError("❌ SUPABASE_URL ou SUPABASE_SERVICE_KEY não encontradas no .env")

supabase: Client = create_client(URL, KEY)

# Aliases for backward compatibility
db_client = supabase
DatabaseClient = supabase

def save_alerts(alerts_data: list):
    """Insere ou atualiza uma lista de alertas no Supabase."""
    try:
        # upsert: se o id já existir, atualiza; se não, cria.
        data, count = supabase.table('threat_alerts').upsert(
            alerts_data, 
            on_conflict="id" # Define a coluna ID como o verificador de conflito
        ).execute()
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar no Supabase: {e}")
        return False
