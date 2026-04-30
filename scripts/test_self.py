import os
import instaloader
from dotenv import load_dotenv

load_dotenv()

L = instaloader.Instaloader()
ig_user = os.getenv('IG_USER')

try:
    L.load_session_from_file(username=ig_user, filename='sentinela_ig_session')
    print(f'✅ Sessão para @{ig_user} carregada.')
except Exception as e:
    print(f"❌ Falha ao carregar sessão: {e}")
    exit(1)

print(f'🔍 Testando busca do PRÓPRIO perfil: @{ig_user}...')
try:
    profile = instaloader.Profile.from_username(L.context, ig_user)
    print(f'🏆 SUCESSO! Encontrado: {profile.full_name}')
except Exception as e:
    print(f"❌ Erro ao buscar @{ig_user}: {e}")
