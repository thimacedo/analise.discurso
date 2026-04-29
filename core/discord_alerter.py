import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_alert(title: str, message: str, color: int = 16711680): # Vermelho por padrão
    """
    Envia alerta crítico para o Discord.
    Cores: Vermelho = 16711680 | Laranja = 16753920 | Verde = 32768
    """
    if not WEBHOOK_URL:
        print("⚠️ Discord Webhook não configurado. Alerta ignorado.")
        return

    payload = {
        "username": "Sentinela Democrática",
        "avatar_url": "https://img.icons8.com/3d-fluency/94/shield.png", # Ícone de escudo
        "embeds": [{
            "title": title,
            "description": message,
            "color": color,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Erro ao enviar alerta Discord: {e}")
