import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
supa = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def clear_synthetic():
    print("🧹 Iniciando limpeza de comentários sintéticos...")
    
    # Busca comentários que começam com 'synth_'
    try:
        # No Supabase/Postgrest, usamos 'like' ou 'ilike' para filtros parciais
        res = supa.table('comentarios').delete().like('id_externo', 'synth_%').execute()
        
        # A contagem de itens deletados nem sempre é retornada diretamente dependendo da config do Supabase
        # Mas o execute() lança erro se falhar.
        print(f"✅ Limpeza concluída com sucesso.")
        
    except Exception as e:
        print(f"❌ Erro ao deletar: {e}")

if __name__ == "__main__":
    clear_synthetic()
