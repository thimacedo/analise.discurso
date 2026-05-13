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

def get_next_targets_to_scrape(limit: int = 5) -> list:
    """Busca os alvos mais prioritários e que não foram raspados recentemente."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('candidatos') \
            .select('username, prioridade_coleta') \
            .ilike('status_monitoramento', 'ATIVO') \
            .order('prioridade_coleta', desc=True) \
            .order('last_scraped_at', desc=False) \
            .limit(limit) \
            .execute()
        
        # Retorna apenas os usernames, garantindo que não tenham @ no início
        return [item['username'].lstrip('@') for item in response.data]
    except Exception as e:
        print(f"❌ Erro ao buscar alvos no banco: {e}")
        return []

def update_last_scraped_at(username: str):
    """Atualiza o timestamp de raspagem para esfriar o alvo na fila."""
    try:
        supabase = get_supabase_client()
        supabase.table('candidatos') \
            .update({'last_scraped_at': 'NOW()'}) \
            .eq('username', username) \
            .execute()
    except Exception as e:
        print(f"❌ Erro ao atualizar last_scraped_at para @{username}: {e}")

def save_comments(comments_data: list):
    """Insere ou atualiza comentários extraídos na tabela 'comentarios'."""
    try:
        supabase = get_supabase_client()
        data, count = supabase.table('comentarios').upsert(
            comments_data, 
            on_conflict="id_externo" # Evita duplicatas baseado no ID externo gerado
        ).execute()
        return True
    except Exception as e:
        print(f"❌ Erro ao salvar comentários no Supabase: {e}")
        return False

def save_scrape_error(username: str, error_type: str):
    """Registra uma falha de raspagem para análise de resiliência."""
    try:
        supabase = get_supabase_client()
        # Aqui poderíamos ter uma tabela 'scrape_errors' ou atualizar a 'candidatos'
        # Por enquanto, vamos apenas logar e talvez atualizar um campo de erro na tabela candidatos se existir
        print(f"⚠️ Registrando erro {error_type} para @{username}")
        # Exemplo: supabase.table('candidatos').update({'last_error': error_type}).eq('username', username).execute()
    except Exception as e:
        print(f"❌ Erro ao registrar falha para @{username}: {e}")
