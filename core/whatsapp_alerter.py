import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

PHONE = os.getenv("WHATSAPP_PHONE")
API_KEY = os.getenv("WHATSAPP_API_KEY")

def send_whatsapp_summary(summary_text: str):
    """Envia UM resumo executivo ao final da pipeline via WhatsApp."""
    if not PHONE or not API_KEY:
        print("⚠️ WhatsApp não configurado. Resumo ignorado.")
        return

    formatted_message = (
        f"🛡️ *SENTINELA - RESUMO DE INTELIGÊNCIA* 🛡️\n\n"
        f"{summary_text}\n\n"
        f"_Pipeline PASA Diamond v19.7.0_"
    )
    
    try:
        encoded_msg = urllib.parse.quote(formatted_message)
        url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={encoded_msg}&apikey={API_KEY}"
        
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            print("✅ Resumo executivo enfileirado para envio no WhatsApp.")
        else:
            print(f"⚠️ Erro ao enfileirar WhatsApp: {response.text}")
    except Exception as e:
        print(f"❌ Falha na requisição do WhatsApp: {e}")
