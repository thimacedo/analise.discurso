import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

PHONE = os.getenv("WHATSAPP_PHONE")
API_KEY = os.getenv("WHATSAPP_API_KEY")

def send_whatsapp_alert(message: str):
    """
    Envia alerta via WhatsApp usando CallMeBot API.
    """
    if not PHONE or not API_KEY:
        print("⚠️ WhatsApp (CallMeBot) não configurado. Alerta ignorado.")
        return

    try:
        encoded_msg = urllib.parse.quote(message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={encoded_msg}&apikey={API_KEY}"
        
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            print(f"⚠️ Erro ao enviar WhatsApp: {response.text}")
    except Exception as e:
        print(f"🔥 Falha na conexão WhatsApp: {e}")
