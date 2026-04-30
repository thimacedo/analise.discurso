import os
import time
import instaloader
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, UTC

load_dotenv()

# Inicializa Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class InstagramFortress:
    def __init__(self):
        # Configuração do Instaloader: Não baixa mídias, apenas dados textuais
        self.L = instaloader.Instaloader(
            download_videos=False, 
            download_pictures=False, 
            save_metadata=False,
            max_connection_attempts=3,
            request_timeout=30
        )
        self.session_file = "sentinela_ig_session"
        
    def login(self):
        """Faz login seguro e salva a sessão local para não precisar repetir."""
        ig_user = os.getenv("IG_USER")
        ig_pass = os.getenv("IG_PASS")
        
        if not ig_user:
            print("❌ Configure IG_USER e IG_PASS no .env")
            return False

        try:
            # Tenta carregar sessão salva (se já tiver logado antes)
            self.L.load_session_from_file(username=ig_user, filename=self.session_file)
            print(f"✅ Sessão local para @{ig_user} carregada.")
        except FileNotFoundError:
            # Primeiro acesso: Faz login com user/senha
            print(f"🔑 Primeiro login com a conta burner @{ig_user}...")
            
            if not ig_pass:
                print("❌ Senha IG_PASS não encontrada no .env")
                return False
                
            try:
                self.L.login(ig_user, ig_pass)
                self.L.save_session_to_file(filename=self.session_file)
                print("✅ Login realizado e sessão salva localmente!")
            except instaloader.exceptions.TwoFactorAuthRequiredException:
                # Se o Instagram pedir código SMS/Auth App
                print("🔒 O Instagram pediu código 2FA.")
                print("⚠️  AVISO: Como estou em modo automatizado, você precisa rodar este script manualmente uma vez para digitar o código 2FA.")
                return False
            except Exception as e:
                print(f"❌ Falha no login: {e}")
                return False
                
        return True

    def scrape_targets(self, limit=15):
        """Busca alvos pendentes e raspa comentários."""
        if not self.login():
            return
            
        # 1. Busca alvos no banco que ainda não foram raspados
        # Nota: Ajustado para usar .is_('last_scraped_at', 'null') conforme solicitado
        try:
            response = supabase.table('candidatos')\
                .select('id, username')\
                .is_('last_scraped_at', 'null')\
                .limit(limit)\
                .execute()
        except Exception as e:
            print(f"❌ Erro ao buscar alvos: {e}")
            return
            
        targets = response.data
        if not targets:
            print("✅ Nenhum alvo pendente no Instagram.")
            return
            
        print(f"🎯 Raspando {len(targets)} alvos do Instagram...")
        
        for target in targets:
            username = target['username']
            candidato_id = target['id']
            print(f"\n  -> Extraindo: @{username}")
            
            try:
                profile = instaloader.Profile.from_username(self.L.context, username)
                
                # 2. Atualiza dados do perfil
                supabase.table('candidatos').update({
                    'seguidores': profile.followers,
                    'last_scraped_at': datetime.now(UTC).isoformat()
                }).eq('id', candidato_id).execute()
                
                # 3. Pega os últimos 3 posts
                post_counter = 0
                for post in profile.get_posts():
                    if post_counter >= 3:
                        break
                        
                    # 4. Pega os primeiros 50 comentários de cada post
                    comment_counter = 0
                    try:
                        for comment in post.get_comments():
                            if comment_counter >= 50:
                                break
                                
                            comment_data = {
                                'candidato_id': username, # FK usa username no schema atual da view
                                'post_id': post.shortcode,
                                'autor_username': comment.owner.username,
                                'texto_bruto': comment.text,
                                'plataforma': 'INSTAGRAM',
                                'data_coleta': datetime.now(UTC).isoformat(),
                                'processado_ia': False,
                                'id_externo': f"ig_{comment.id}" # ID único para evitar duplicatas
                            }
                            
                            try:
                                # Usamos insert. O banco protege contra duplicatas via id_externo UNIQUE
                                supabase.table('comentarios').insert(comment_data).execute()
                                comment_counter += 1
                            except Exception:
                                pass # Ignora duplicatas
                                
                        print(f"     📹 Post {post.shortcode}: {comment_counter} comentários salvos.")
                        post_counter += 1
                    except Exception as e:
                        print(f"     ⚠️ Erro nos comentários do post {post.shortcode}: {e}")
                        
                    time.sleep(3) # Pausa entre posts (Anti-Ban)
                    
                time.sleep(5) # Pausa entre perfis (Anti-Ban)
                
            except instaloader.exceptions.LoginRequiredException:
                print("🚫 Sessão expirada. Delete o arquivo 'sentinela_ig_session' e rode novamente.")
                break
            except instaloader.exceptions.ProfileNotExistsException:
                print(f"⚠️ Perfil @{username} não existe ou é privado.")
                # Marca como raspado para não tentar de novo
                supabase.table('candidatos').update({'last_scraped_at': datetime.now(UTC).isoformat()}).eq('id', candidato_id).execute()
            except Exception as e:
                print(f"❌ Erro em @{username}: {e}")

if __name__ == "__main__":
    scraper = InstagramFortress()
    scraper.scrape_targets(limit=15)
