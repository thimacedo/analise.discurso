import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

PHONE = os.getenv("WHATSAPP_PHONE")
API_KEY = os.getenv("WHATSAPP_API_KEY")

from core.firebase_alerter import send_alert_summary

def send_whatsapp_summary(summary_text: str):
    """Encaminha para a nova infraestrutura de alertas via Firebase."""
    send_alert_summary(summary_text)

