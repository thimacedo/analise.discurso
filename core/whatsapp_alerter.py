import logging
from core.firebase_alerter import send_alert_summary

logger = logging.getLogger("sentinela-whatsapp-legacy")

def send_whatsapp_summary(summary_text: str):
    """
    Interface legado para envio de alertas. 
    Encaminha todas as chamadas para a nova infraestrutura Firebase Push.
    """
    logger.info("Redirecionando alerta legado para Firebase Push.")
    send_alert_summary(summary_text)
