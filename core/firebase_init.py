import os
import json
import firebase_admin
from firebase_admin import credentials
import logging

logger = logging.getLogger("sentinela-firebase")

def initialize_firebase():
    """Inicializa o Firebase Admin SDK usando a variável de ambiente FIREBASE_SERVICE_ACCOUNT_JSON."""
    try:
        # Verifica se já está inicializado
        if firebase_admin._apps:
            return firebase_admin.get_app()

        cred_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
        if not cred_json:
            logger.warning("⚠️ FIREBASE_SERVICE_ACCOUNT_JSON não encontrada. Notificações push desativadas.")
            return None

        # Carrega as credenciais do JSON string
        cred_dict = json.loads(cred_json)
        cred = credentials.Certificate(cred_dict)
        
        app = firebase_admin.initialize_app(cred)
        logger.info("✅ Firebase Admin SDK inicializado com sucesso.")
        return app
    except Exception as e:
        logger.error(f"❌ Falha ao inicializar Firebase Admin SDK: {e}")
        return None

# Singleton do app
admin_app = initialize_firebase()
