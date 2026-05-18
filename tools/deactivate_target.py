import os
import sys
from dotenv import load_dotenv

# Garante que o diretório raiz do projeto esteja no path para imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from core.supabase_service import supabase
except ImportError:
    print("❌ Erro: Não foi possível importar o serviço do Supabase. Verifique o PYTHONPATH.")
    sys.exit(1)

def deactivate_target(username: str):
    """
    Altera o status de monitoramento de um alvo para 'Inativo' no banco de dados.
    """
    if not username:
        print("❌ Username não fornecido.")
        return

    try:
        print(f"🔄 Desativando monitoramento para o alvo: @{username}...")
        
        # A sintaxe do Supabase-py v2 retorna um objeto com 'data' e 'count'
        response = supabase.table('candidatos').update({
            'status_monitoramento': 'Inativo'
        }).eq('username', username).execute()

        # Acessa o 'count' dentro do objeto de resposta
        count = response.count

        if count is not None and count > 0:
            print(f"✅ Sucesso: {count} registro(s) para @{username} foram marcados como 'Inativo'.")
        else:
            print(f"⚠️ Atenção: Nenhum alvo com o username @{username} foi encontrado para atualização.")

    except Exception as e:
        print(f"❌ Erro crítico ao conectar ou atualizar o Supabase: {e}")

if __name__ == "__main__":
    # Pega o alvo do argumento da linha de comando, se houver, senão usa o padrão
    target_to_deactivate = sys.argv[1] if len(sys.argv) > 1 else "claudiocastrooficial"
    deactivate_target(target_to_deactivate)
