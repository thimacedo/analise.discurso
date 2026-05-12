# core/supabase_service.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()
class SupabaseService:
    """
    Serviço centralizado de conexão com o Supabase (Singleton com Lazy Loading).
    Garante que o client só seja criado quando necessário, evitando crashes no Pytest.
    """
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseService, cls).__new__(cls)
            cls._instance._client = None
        return cls._instance
    def get_client(self) -> Client:
        """Retorna o cliente Supabase. Conecta apenas na primeira chamada."""
        if self._client is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_SERVICE_KEY")
            if not url or not key:
                raise ValueError("❌ SUPABASE_URL ou SUPABASE_SERVICE_KEY não encontradas no .env")
            self._client = create_client(url, key)
            print("✅ Conexão com Supabase estabelecida (Lazy Load).")
        return self._client
# Função de conveniência para não precisar instanciar a classe em todo lugar
def get_supabase_client() -> Client:
    return SupabaseService().get_client()
# Mantendo a função de salvamento aqui para facilitar a vida do Worker
def save_alerts(alerts_data: list):
    """Insere ou atualiza uma lista de alertas no Supabase."""
    try:
        supabase = get_supabase_client()
        data, count = supabase.table('threat_alerts').upsert(
            alerts_data,
            on_conflict="id"
        ).execute()
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar no Supabase: {e}")
        return False
