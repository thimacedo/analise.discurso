import stripe
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def validate_restricted_key():
    print("--- Stripe Restricted Key Validation (Products/Prices) ---")
    
    api_key = os.getenv('STRIPE_API_KEY')
    if not api_key:
        print("[ERROR] STRIPE_API_KEY missing.")
        sys.exit(1)
        
    print(f"[INFO] Key prefix: {api_key[:10]}...")
    stripe.api_key = api_key
    
    try:
        # Products
        products = stripe.Product.list(limit=5)
        print(f"[OK] Products accessible. Found: {len(products.data)}")
        
        # Prices
        prices = stripe.Price.list(limit=5)
        print(f"[OK] Prices accessible. Found: {len(prices.data)}")
        
        return True
    except stripe.error.PermissionError as e:
        print(f"[ERROR] Permission denied: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Unexpected: {str(e)}")
    
    return False

if __name__ == "__main__":
    if validate_restricted_key():
        print("\n--- VALIDATION SUCCESSFUL ---")
        sys.exit(0)
    print("\n--- VALIDATION FAILED ---")
    sys.exit(1)
