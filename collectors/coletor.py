import os
import time
import random
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ========================================================
# 1. COLETOR SEGURO (Usa login apenas para listar seguidos)
# ========================================================
try:
    from instagrapi import Client
    INSTAGRAPI_OK = True
except ImportError:
    INSTAGRAPI_OK = False

class ColetorSeguro:
    def __init__(self, session_file="session.json"):
        if not INSTAGRAPI_OK:
            raise ImportError("Biblioteca 'instagrapi' não instalada. Rode: pip install instagrapi")
        self.client = Client()
        self.session_file = session_file
        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")
    
    def log(self, msg):
        msg_limpa = msg.encode('ascii', 'ignore').decode('ascii')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Seguro] {msg_limpa}")

    def login(self):
        if os.path.exists(self.session_file):
            try:
                self.client.load_settings(self.session_file)
                self.client.get_timeline_feed()
                self.log("Sessao carregada.")
                return
            except Exception:
                self.log("Sessao expirada. Fazendo novo login...")

        if not self.username or not self.password:
            self.log("Erro: IG_USERNAME ou IG_PASSWORD nao configurados.")
            return

        self.client.login(self.username, self.password)
        self.client.dump_settings(self.session_file)
        self.log("Login realizado.")
    
    def obter_perfis_seguidos(self):
        self.login()
        self.log("Buscando perfis seguidos...")
        try:
            seguindo = self.client.user_following(self.client.user_id)
            return [s.username for s in seguindo.values()]
        except Exception as e:
            self.log(f"Erro ao buscar seguidos: {e}")
            return []


# ========================================================
# 2. COLETOR PÚBLICO (Usa instaloader + sessão para evitar 403)
# ========================================================
try:
    import instaloader
    INSTALOADER_OK = True
except ImportError:
    INSTALOADER_OK = False

class ColetorPublico:
    def __init__(self, session_file="session.json"):
        if not INSTALOADER_OK:
            raise ImportError("Biblioteca 'instaloader' não instalada. Rode: pip install instaloader")
        self.L = instaloader.Instaloader(
            download_videos=False,
            download_pictures=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern="",
            sleep=True, 
            max_connection_attempts=3
        )
        
        self.session_file = session_file
        self.ig_username = os.getenv("IG_USERNAME")
        if os.path.exists(self.session_file) and self.ig_username:
            try:
                # Importante: Instaloader precisa carregar a sessão para o usuário correto
                self.L.load_session_from_file(self.ig_username, filename=self.session_file)
                self.log("Instaloader carregou a sessao (Blindado contra 403).")
            except Exception as e:
                self.log(f"Aviso: Nao foi possivel carregar sessao no Instaloader: {e}")
        else:
            self.log("Aviso: Sessao ou Usuario nao encontrados. Rode 'python atualizar_perfis.py'.")

    def log(self, msg):
        msg_limpa = msg.encode('ascii', 'ignore').decode('ascii')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Coletor] {msg_limpa}")

    def coletar_comentarios_perfil(self, username, posts_limit=2):
        self.log(f"Acessando perfil: @{username}")
        todos = []
        
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
            posts = profile.get_posts()
            count = 0
            
            for post in posts:
                if count >= posts_limit:
                    break
                
                code = post.shortcode
                url = f"https://www.instagram.com/p/{code}/"
                self.log(f"    Lendo post {code}...")

                try:
                    for comment in post.get_comments():
                        todos.append({
                            "candidato": username,
                            "texto": comment.text,
                            "autor_username": comment.owner.username,
                            "timestamp": comment.created_at_utc.isoformat(),
                            "post_url": url,
                            "post_caption": post.caption or "",
                            "likes_comentario": getattr(comment, 'likes_count', 0)
                        })
                    
                    count += 1
                    self.log(f"    - {len(todos)} comentarios coletados ate agora.")
                    time.sleep(random.uniform(8, 15))
                    
                except instaloader.exceptions.ConnectionException as e:
                    if "429" in str(e) or "rate limit" in str(e).lower():
                        self.log("    Rate Limit (429). Pausa de 15min.")
                        time.sleep(900)
                    else:
                        self.log(f"    Erro de conexao: {e}")
                        break
                except Exception as e:
                    self.log(f"    Erro no post: {e}")
                    break
                    
        except instaloader.exceptions.ProfileNotExistsException:
            self.log(f"Perfil @{username} nao existe ou e privado.")
        except instaloader.exceptions.ConnectionException as e:
            self.log(f"Erro de conexao geral em @{username}: {e}")
        except Exception as e:
            self.log(f"Erro inesperado em @{username}: {e}")
            
        return todos

    def coletar_todos(self, arquivo_perfis="perfis_monitorados.json", posts_por_perfil=2):
        if not os.path.exists(arquivo_perfis):
            self.log("Arquivo de perfis nao encontrado. Rode 'python atualizar_perfis.py' primeiro.")
            return pd.DataFrame()

        with open(arquivo_perfis, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            perfis = dados.get("perfis", [])

        self.log(f"Iniciando coleta para {len(perfis)} perfis.")
        todos_dados = []
        
        for i, perfil in enumerate(perfis, 1):
            self.log(f"=== Coletando {i}/{len(perfis)}: @{perfil} ===")
            try:
                dados_perfil = self.coletar_comentarios_perfil(perfil, posts_limit=posts_por_perfil)
                todos_dados.extend(dados_perfil)
            except Exception as e:
                self.log(f"Erro critico ao processar @{perfil}: {e}")
            
            if i < len(perfis):
                pausa = random.uniform(45, 90)
                self.log(f"Aguardando {pausa:.1f}s antes do proximo perfil...")
                time.sleep(pausa)
                
        if todos_dados:
            df_final = pd.DataFrame(todos_dados)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome = f"dados_brutos_{timestamp}.csv"
            df_final.to_csv(nome, index=False, encoding="utf-8-sig")
            self.log(f"Dados salvos em {nome} ({len(df_final)} comentarios)")
            return df_final
            
        self.log("Nenhum comentario coletado no total.")
        return pd.DataFrame()