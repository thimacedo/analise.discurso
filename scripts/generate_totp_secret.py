import pyotp
import qrcode
import os

def generate():
    # Gera um segredo aleatório
    secret = pyotp.random_base32()
    print("\n" + "="*60)
    print("🔐 SEGURANÇA SENTINELA | SISTEMA INDEPENDENTE")
    print("="*60)
    print(f"1. Sua chave secreta: {secret}")
    print(f"2. Salve no .env: SENTINELA_ADMIN_TOTP_SECRET={secret}")
    print("="*60)
    
    # Identidade correta do Sentinela
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name="Gestao_Alvos", 
        issuer_name="Sentinela_Intel"
    )
    
    img = qrcode.make(uri)
    # Remove o anterior se existir
    if os.path.exists("admin_qr_code.png"):
        os.remove("admin_qr_code.png")
        
    img.save("sentinela_auth_qr.png")
    print(f"\n✅ NOVO QR Code gerado!")
    print(f"📂 Arquivo: {os.path.abspath('sentinela_auth_qr.png')}")
    print("📱 Escaneie com o Google Authenticator (Aparecerá como 'Sentinela_Intel')")
    print("="*60 + "\n")

if __name__ == "__main__":
    generate()
