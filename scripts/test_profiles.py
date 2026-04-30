import os
import instaloader
from dotenv import load_dotenv

load_dotenv()

L = instaloader.Instaloader()

# Tenta carregar a sessão que acabamos de salvar
ig_user = os.getenv('IG_USER')
try:
    L.load_session_from_file(username=ig_user, filename='sentinela_ig_session')
    print(f'✅ Sessão para @{ig_user} carregada.')
except Exception as e:
    print(f"❌ Falha ao carregar sessão: {e}")
    exit(1)

test_profiles = ['lulaoficial', 'jairmessiasbolsonaro', 'cirogomes']

for user in test_profiles:
    print(f'🔍 Testando busca de perfil: @{user}...')
    try:
        profile = instaloader.Profile.from_username(L.context, user)
        print(f'🏆 SUCESSO! Encontrado: {profile.full_name} - Seguidores: {profile.followers}')
        break
    except Exception as e:
        print(f"⚠️ Erro ao buscar @{user}: {e}")
