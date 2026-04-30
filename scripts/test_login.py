import os
import instaloader
from dotenv import load_dotenv

load_dotenv()

L = instaloader.Instaloader()

print('🔑 Iniciando login forçado...')
ig_user = os.getenv('IG_USER')
ig_pass = os.getenv('IG_PASS')

if not ig_user or not ig_pass:
    print("❌ Erro: IG_USER ou IG_PASS não configurados no .env")
    exit(1)

try:
    L.login(ig_user, ig_pass)
    print('✅ Login básico feito!')
except instaloader.exceptions.TwoFactorAuthRequiredException:
    print('🔒 O Instagram exige código 2FA.')
    code = input('🔒 Digite o código 2FA do Instagram: ')
    try:
        L.two_factor_login(code)
        print('✅ 2FA validado!')
    except Exception as e:
        print(f"❌ Erro no 2FA: {e}")
        exit(1)
except Exception as e:
    print(f"❌ Falha no login: {e}")
    exit(1)

L.save_session_to_file(filename='sentinela_ig_session')
print('✅ Sessão salva em "sentinela_ig_session".')

print('🔍 Testando busca de perfil real (@cirogomes)...')
try:
    profile = instaloader.Profile.from_username(L.context, 'cirogomes')
    print(f'🏆 SUCESSO! Encontrado: {profile.full_name} - Seguidores: {profile.followers}')
except Exception as e:
    print(f"❌ Erro ao buscar perfil: {e}")
