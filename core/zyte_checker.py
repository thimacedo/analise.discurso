"""
PASA v49.9 - Zyte Connection Checker
Verifica a integridade da conexão com Zyte API para o Watchdog.
"""
import httpx
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("ZyteChecker")

def check_zyte_health():
    """Valida se a chave do Zyte está ativa e se há conectividade."""
    zyte_key = os.getenv("ZYTE_API_KEY")
    if not zyte_key:
        return False, "ZYTE_API_KEY ausente no .env"
    
    url = "https://api.zyte.com/v1/extract"
    payload = {
        "url": "https://toscrape.com",
        "httpResponseBody": True
    }
    
    try:
        # Usamos um timeout curto para o watchdog não travar
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                url,
                auth=(zyte_key, ""),
                json=payload
            )
            
            if response.status_code == 200:
                return True, "Conectado"
            else:
                return False, f"Erro {response.status_code}: {response.text[:50]}"
                
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    status, msg = check_zyte_health()
    print(f"Status: {status} | Msg: {msg}")
