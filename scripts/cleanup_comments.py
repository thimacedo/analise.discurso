import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def cleanup():
    print("Iniciando limpeza de comentários inválidos...")
    
    # Exemplo: deletar comentários onde texto_bruto é muito curto ou igual ao autor_username
    # Como o Supabase client não tem .delete() muito flexível com OR complexos, vamos buscar e iterar
    try:
        # Buscar tudo (paginado se for muito, mas vamos pegar os mais recentes)
        res = supabase.table('comentarios').select('id, autor_username, texto_bruto').execute()
        
        deleted_count = 0
        for comment in res.data:
            autor = comment.get('autor_username', '')
            texto = comment.get('texto_bruto', '')
            
            # Condições de invalidez
            if not texto or len(texto.strip()) < 3 or texto.strip().lower() == autor.strip().lower():
                # Deletar este ID
                supabase.table('comentarios').delete().eq('id', comment['id']).execute()
                deleted_count += 1
                
        print(f"Limpeza concluída. {deleted_count} comentários inválidos foram removidos.")
    except Exception as e:
        print(f"Erro durante a limpeza: {e}")

if __name__ == "__main__":
    cleanup()
