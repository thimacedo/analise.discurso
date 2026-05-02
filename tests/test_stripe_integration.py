import stripe
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def test_stripe_connection():
    print("--- Iniciando Teste Formal de Integração Stripe ---")
    
    api_key = os.getenv('STRIPE_API_KEY')
    
    if not api_key:
        print("[ERRO] STRIPE_API_KEY não encontrada no ambiente.")
        sys.exit(1)
        
    if not api_key.startswith('rk_test_'):
        print(f"[AVISO] A chave fornecida não parece ser uma Restricted Test Key: {api_key[:10]}...")
    else:
        print("[OK] Chave identificada como Restricted Test Key.")

    stripe.api_key = api_key
    
    try:
        print("Tentando listar clientes (limit=1)...")
        customers = stripe.Customer.list(limit=1)
        print(f"[SUCESSO] Conexão estabelecida. Clientes encontrados: {len(customers.data)}")
        print(f"Detalhes do objeto: {customers.object}")
        return True
    except stripe.error.AuthenticationError:
        print("[ERRO] Falha de autenticação. Verifique sua STRIPE_API_KEY.")
    except stripe.error.PermissionError:
        print("[ERRO] A chave não tem permissão para listar clientes.")
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro inesperado: {str(e)}")
    
    return False

if __name__ == "__main__":
    success = test_stripe_connection()
    if success:
        print("--- Teste Concluído com Sucesso ---")
        sys.exit(0)
    else:
        print("--- Teste Falhou ---")
        sys.exit(1)
