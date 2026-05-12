
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import json
import firebase_admin
from firebase_admin import credentials
import logging

logger = logging.getLogger("sentinela-firebase")

def get_firebase_app():
    """Retorna o app Firebase inicializado ou None se as chaves estiverem faltando."""
    try:
        if firebase_admin._apps:
            return firebase_admin.get_app()

        cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if not cred_json:
            return None

        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)

        return firebase_admin.initialize_app(cred)
    except Exception as e:
        logger.error(f"⚠️ Falha ao inicializar Firebase: {e}")
        return None

# Manter admin_app para compatibilidade, mas usando o getter
admin_app = get_firebase_app()
