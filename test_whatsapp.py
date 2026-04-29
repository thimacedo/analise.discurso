import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

PHONE = os.getenv("WHATSAPP_PHONE")
API_KEY = os.getenv("WHATSAPP_API_KEY")

mensagem = (
    "🛡️ *SENTINELA DEMOCRÁTICA - TESTE* 🛡️\n\n"
    "Integração WhatsApp funcionando perfeitamente!\n"
    "A Munição Forense está pronta para disparar.\n\n"
    "_Pipeline PASA v19.7.0_"
)

if not PHONE or not API_KEY:
    print("❌ Erro: WHATSAPP_PHONE ou WHATSAPP_API_KEY não encontrados no .env")
    print("Certifique-se de que você configurou o seu arquivo .env corretamente.")
else:
    encoded_msg = urllib.parse.quote(mensagem)
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={encoded_msg}&apikey={API_KEY}"

    print(f"Enviando teste de inteligência para {PHONE}...")
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            print("✅ Sucesso! Verifique o seu WhatsApp.")
        else:
            print(f"❌ Falha: {response.text}")
    except Exception as e:
        print(f"🔥 Erro de conexão: {e}")
