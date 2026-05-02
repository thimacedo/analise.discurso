import os
import json
from firebase_admin import messaging
from core.firebase_init import adminApp # Preciso criar este arquivo ou ajustar a config

# NOTA: Ajuste de configuração para usar o Admin SDK criado anteriormente
from src.services.firebaseConfig import adminApp

def send_firebase_push_notification(title: str, body: str, topic: str = "sentinela_alerts"):
    """Envia uma notificação push via Firebase Cloud Messaging."""
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            topic=topic,
        )
        response = messaging.send(message)
        print(f"✅ Notificação enviada com sucesso: {response}")
    except Exception as e:
        print(f"❌ Erro ao enviar notificação via Firebase: {e}")

def send_alert_summary(summary_text: str):
    """Substitui o alerta do WhatsApp por Firebase Push."""
    print("🛡️ Enviando Resumo de Inteligência via Firebase Push...")
    send_firebase_push_notification(
        title="🛡️ SENTINELA - RESUMO DE INTELIGÊNCIA",
        body=summary_text
    )
