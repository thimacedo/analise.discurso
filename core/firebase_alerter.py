import logging
from firebase_admin import messaging
from core.firebase_init import admin_app
from supabase import Client
import os

logger = logging.getLogger("sentinela-alerter")

def get_supa():
    """Importação tardia para evitar loops de dependência."""
    from api.index import get_supa as get_supabase_client
    return get_supa_client()

def send_firebase_push_notification(tokens: list, title: str, body: str, data: dict = None):
    """Envia uma notificação push via FCM para uma lista de tokens."""
    if not admin_app or not tokens:
        return

    try:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
            tokens=tokens,
        )
        response = messaging.send_multicast(message)
        logger.info(f"✅ Notificações enviadas: {response.success_count} sucesso, {response.failure_count} falhas.")
        
        # Opcional: Lógica para remover tokens inválidos do banco
        if response.failure_count > 0:
            for index, resp in enumerate(response.responses):
                if not resp.success:
                    # Token inválido ou expirado
                    logger.warning(f"Token inválido detectado no índice {index}: {resp.exception}")
                    
    except Exception as e:
        logger.error(f"❌ Erro ao enviar notificações via FCM: {e}")

def send_push_to_user(user_id: str, title: str, body: str, data: dict = None):
    """Busca os tokens de um usuário no Supabase e envia a notificação."""
    try:
        # Usamos uma importação local para evitar circular dependencies com api.index
        from supabase import create_client
        supa = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        
        res = supa.table('user_push_tokens').select('token').eq('user_id', user_id).execute()
        tokens = [r['token'] for r in res.data] if res.data else []
        
        if tokens:
            send_firebase_push_notification(tokens, title, body, data)
        else:
            logger.info(f"Nenhum token de push encontrado para o usuário {user_id}")
    except Exception as e:
        logger.error(f"Erro ao processar push para usuário {user_id}: {e}")

def send_alert_summary(summary_text: str):
    """Interface legada mantida para compatibilidade, agora enviando via FCM para um tópico global ou admin."""
    logger.info("🛡️ Enviando Resumo de Inteligência via Firebase Push...")
    
    # Por enquanto envia para um tópico 'admin_alerts'
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title="🛡️ SENTINELA - ALERTA DE ÓDIO",
                body=summary_text
            ),
            topic="admin_alerts",
        )
        messaging.send(message)
    except Exception as e:
        logger.error(f"Erro ao enviar alerta global: {e}")
