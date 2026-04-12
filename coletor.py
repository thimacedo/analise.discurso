import os
import time
import random
import requests
import pandas as pd
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientThrottledError, RateLimitError, ChallengeRequired
from dotenv import load_dotenv
from memoria import MemoriaExecucao

load_dotenv()

class ColetorSeguro:
    def __init__(self, session_file="session.json"):
        self.client = Client()
        self.session_file = session_file
        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")
        self.memoria = MemoriaExecucao()
        if not self.username or not self.password:
            raise ValueError("IG_USERNAME ou IG_PASSWORD não configurados.")

    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Coletor] {msg}")

    def login(self):
        if os.path.exists(self.session_file):
            try:
                self.client.load_settings(self.session_file)
                self.client.get_timeline_feed()
                self.log("✅ Sessão carregada com sucesso.")
                return
            except Exception:
                self.log("⚠️ Sessão expirada. Tentando novo login...")
        try:
            self.client.login(self.username, self.password)
            self.client.dump_settings(self.session_file)
            self.log("✅ Novo login realizado e sessão salva.")
        except ChallengeRequired as e:
            self.log("⚠️ Instagram requer desafio/2FA. Digite o código (se for 2FA) ou resolva o desafio no app.")
            # Se for 2FA, a mensagem pode indicar; neste caso, pedimos o código
            # A instagrapi lida com 2FA automaticamente se você passar verification_code
            # Vamos pedir o código e tentar novamente:
            code = input("Digite o código de autenticação (2FA): ")
            self.client.login(self.username, self.password, verification_code=code)
            self.client.dump_settings(self.session_file)
            self.log("✅ Login com 2FA realizado.")
        except Exception as e:
            if "Two-factor authentication required" in str(e):
                code = input("⚠️ Digite o código de 2FA: ")
                self.client.login(self.username, self.password, verification_code=code)
                self.client.dump_settings(self.session_file)
                self.log("✅ Login com 2FA realizado.")
            else:
                raise e

    def coletar_comentarios_perfil(self, username, posts_limit=10, comments_per_post=200):
        self.log(f"🐦 Coletando @{username}...")
        
        # Consulta memória para este perfil
        posts_ja_coletados = self.memoria.get_posts_coletados(username)
        ultimo_ts = self.memoria.get_ultimo_timestamp(username)
        
        tentativas_perfil = 0
        max_tentativas = 3
        medias = []
        while tentativas_perfil < max_tentativas:
            try:
                user_id = self.client.user_id_from_username(username)
                medias = self.client.user_medias(user_id, amount=posts_limit)
                break
            except (RateLimitError, ClientThrottledError):
                tentativas_perfil += 1
                self.log(f"⚠️ Rate limit (429) em @{username}. Pausa de 15min. Tentativa {tentativas_perfil}/{max_tentativas}.")
                time.sleep(900)
            except requests.exceptions.RetryError as e:
                if '429' in str(e):
                    tentativas_perfil += 1
                    self.log(f"⚠️ Erro 429 em @{username}. Pausa de 15min. Tentativa {tentativas_perfil}/{max_tentativas}.")
                    time.sleep(900)
                else:
                    self.log(f"❌ Erro de conexão em @{username}: {e}")
                    return pd.DataFrame()
            except Exception as e:
                self.log(f"❌ Erro ao carregar posts de @{username}: {e}")
                return pd.DataFrame()
        
        if not medias:
            self.log(f"⚠️ Nenhum post encontrado para @{username}.")
            return pd.DataFrame()
        
        # Filtra posts que ainda não foram coletados
        novos_posts = []
        for media in medias:
            if media.code not in posts_ja_coletados:
                novos_posts.append(media)
            else:
                self.log(f"    ⏭️ Post {media.code} já coletado anteriormente. Pulando.")
        
        if not novos_posts:
            self.log(f"    ℹ️ Nenhum post novo para @{username}. Pulando perfil.")
            return pd.DataFrame()
        
        todos = []
        maior_ts = ultimo_ts  # para atualizar o timestamp mais recente
        for media in novos_posts:
            tentativas_media = 0
            while tentativas_media < max_tentativas:
                try:
                    code = media.code
                    url = f"https://www.instagram.com/p/{code}/"
                    comentarios = self.client.media_comments(media.id, amount=comments_per_post)
                    
                    # Se temos um timestamp de referência, filtra apenas comentários mais novos
                    if ultimo_ts:
                        comentarios_filtrados = [c for c in comentarios if c.timestamp > ultimo_ts]
                    else:
                        comentarios_filtrados = comentarios
                    
                    for c in comentarios_filtrados:
                        todos.append({
                            "candidato": username,
                            "texto": c.text,
                            "autor_username": c.user.username,
                            "timestamp": c.timestamp,
                            "post_url": url,
                            "post_caption": media.caption_text or "",
                            "likes_comentario": c.like_count
                        })
                        if maior_ts is None or c.timestamp > maior_ts:
                            maior_ts = c.timestamp
                    
                    self.log(f"    ✓ {len(comentarios_filtrados)} novos comentários do post {code}")
                    # Atualiza memória: marca este post como coletado
                    self.memoria.atualizar_perfil(username, post_coletado=code)
                    time.sleep(random.uniform(2, 6))
                    break
                except (RateLimitError, ClientThrottledError):
                    tentativas_media += 1
                    self.log(f"    ⚠️ Rate limit no post {code}. Pausa de 15min. Tentativa {tentativas_media}/{max_tentativas}.")
                    time.sleep(900)
                except requests.exceptions.RetryError as e:
                    if '429' in str(e):
                        tentativas_media += 1
                        self.log(f"    ⚠️ Erro 429 no post {code}. Pausa de 15min. Tentativa {tentativas_media}/{max_tentativas}.")
                        time.sleep(900)
                    else:
                        break
                except Exception as e:
                    self.log(f"    ❌ Erro no post {code}: {e}")
                    break
        
        # Atualiza timestamp mais recente e último post ID
        if maior_ts:
            self.memoria.atualizar_perfil(username, ultimo_timestamp=maior_ts)
        if novos_posts:
            self.memoria.atualizar_perfil(username, ultimo_post_id=novos_posts[0].code)
        
        # Registra total de novos comentários
        self.memoria.incrementar_total_comentarios(username, len(todos))
        
        self.log(f"  📦 Total de novos comentários de @{username}: {len(todos)}")
        return pd.DataFrame(todos)
