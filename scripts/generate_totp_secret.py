import pyotp
import qrcode
import os

def generate():
    # Gera um segredo aleatório compatível com o Google Authenticator
    secret = pyotp.random_base32()
    print("\n" + "="*60)
    print("🔐 CONFIGURAÇÃO DE SEGURANÇA TOTP")
    print("="*60)
    print(f"1. Sua chave secreta (COPIE ISTO AGORA): {secret}")
    print(f"2. Adicione ao seu arquivo .env:")
    print(f"   SENTINELA_ADMIN_TOTP_SECRET={secret}")
    print("="*60)
    
    # Gera a URI para o QR Code
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name="Sentinela_Admin", 
        issuer_name="InovaSys"
    )
    
    # Gera e salva a imagem do QR Code
    img = qrcode.make(uri)
    img.save("admin_qr_code.png")
    print(f"\n✅ QR Code gerado com sucesso!")
    print(f"📂 Arquivo: {os.path.abspath('admin_qr_code.png')}")
    print("📱 Escaneie este arquivo com o aplicativo Google Authenticator no seu celular.")
    print("="*60 + "\n")

if __name__ == "__main__":
    generate()
