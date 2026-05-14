"""
PASA v30 - Purge: Limpa o banco de dados de comentários lixo históricos
"""
from core.supabase_service import get_supabase_client

# Inicializa o cliente Supabase
db = get_supabase_client()

def purge_garbage():
    print("[Purge] Iniciando limpeza de lixo histórico do banco...")
    
    # Padrões de texto que são inquestionavelmente lixo de UI
    garbage_patterns = [
        "Upload de contatos",
        "e outros",
        "não usuários"
    ]
    
    deleted_count = 0
    for pattern in garbage_patterns:
        # Usando a sintaxe correta do cliente supabase-js ou py
        response = db.table('comentarios').delete().ilike('texto_bruto', f'%{pattern}%').execute()
        if hasattr(response, 'data') and response.data:
            deleted_count += len(response.data)
            
    # Padrões de autor lixo (IDs numéricos longos)
    # A consulta like precisa ser ajustada para o banco se necessário, aqui assume string
    response = db.table('comentarios').delete().like('autor_username', '2%').execute() 
    if hasattr(response, 'data') and response.data:
        deleted_count += len(response.data)
        
    print(f"[Purge] {deleted_count} registros de lixo eliminados do banco. DB limpo.")

if __name__ == "__main__":
    purge_garbage()
