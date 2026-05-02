import stripe
import os
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def validate_restricted_key():
    print("--- Validando Permissões de Chave Restrita (Produtos e Preços) ---")
    
    api_key = os.getenv('STRIPE_API_KEY')
    
    if not api_key:
        print("[ERRO] STRIPE_API_KEY não encontrada no ambiente.")
        sys.exit(1)
        
    print(f"[INFO] Usando chave: {api_key[:10]}...")
    stripe.api_key = api_key
    
    success = True
    
    # 1. Validar Listagem de Produtos
    try:
        print("\nTentando listar produtos (limit=5)...")
        products = stripe.Product.list(limit=5)
        print(f"[SUCESSO] Produtos listados: {len(products.data)}")
        for prod in products.data:
            print(f" - ID: {prod.id} | Nome: {prod.name}")
    except stripe.error.PermissionError:
        print("[ERRO] A chave NÃO tem permissão para listar PRODUTOS.")
        success = False
    except Exception as e:
        print(f"[ERRO] Erro inesperado ao listar produtos: {str(e)}")
        success = False

    # 2. Validar Listagem de Preços
    try:
        print("\nTentando listar preços (limit=5)...")
        prices = stripe.Price.list(limit=5)
        print(f"[SUCESSO] Preços listados: {len(prices.data)}")
        for price in prices.data:
            currency = price.currency.upper()
            amount = price.unit_amount / 100
            print(f" - ID: {price.id} | Produto: {price.product} | Valor: {currency} {amount:.2f}")
    except stripe.error.PermissionError:
        print("[ERRO] A chave NÃO tem permissão para listar PREÇOS.")
        success = False
    except Exception as e:
        print(f"[ERRO] Erro inesperado ao listar preços: {str(e)}")
        success = False
    
    return success

if __name__ == "__main__":
    is_valid = validate_restricted_key()
    if is_valid:
        print("\n--- Validação Concluída com SUCESSO ---")
        sys.exit(0)
    else:
        print("\n--- Validação FALHOU ---")
        sys.exit(1)
