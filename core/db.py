# core/db.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Variável global para armazenar o cliente (Singleton)
_supabase_client = None

def get_supabase_client() -> Client:
    """
    Inicializa e retorna o cliente Supabase apenas quando chamado.
    Isso evita erros de importação no Pytest ou em scripts que não usam o DB.
    """
    global _supabase_client
    if _supabase_client is None:
        URL = os.getenv("SUPABASE_URL")
        KEY = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not URL or not KEY:
            raise ValueError("❌ SUPABASE_URL ou SUPABASE_SERVICE_KEY não encontradas no .env")
            
        _supabase_client = create_client(URL, KEY)
        
    return _supabase_client

class LazySupabaseProxy:
    """
    Proxy que intercepta as chamadas para o client Supabase e faz a inicialização lazy.
    Usado para manter retrocompatibilidade com códigos que importam `db_client` ou `DatabaseClient`.
    """
    def __getattr__(self, name):
        client = get_supabase_client()
        return getattr(client, name)

# Instâncias Lazy (Proxy) para retrocompatibilidade em todo o projeto
db_client = LazySupabaseProxy()
DatabaseClient = LazySupabaseProxy()
supabase = LazySupabaseProxy()

def save_alerts(alerts_data: list):
    """Insere ou atualiza uma lista de alertas no Supabase."""
    try:
        # A conexão só acontece aqui, quando a função é executada de verdade!
        client = get_supabase_client()
        
        data, count = client.table('threat_alerts').upsert(
            alerts_data, 
            on_conflict="id" # Define a coluna ID como o verificador de conflito
        ).execute()
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar no Supabase: {e}")
        return False

