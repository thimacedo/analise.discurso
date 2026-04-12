import os
import time
import random
import requests
import pandas as pd
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientThrottledError, RateLimitError
from dotenv import load_dotenv

load_dotenv()

class ColetorSeguro:
    def __init__(self, session_file="session.json"):
        self.client = Client()
        self.session_file = session_file
        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")
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
        except Exception as e:
            if "Two-factor authentication required" in str(e):
                code = input("⚠️ Digite o código de 2FA: ")
                self.client.login(self.username, self.password, verification_code=code)
                self.client.dump_settings(self.session_file)
                self.log("✅ Login com 2FA realizado.")
            else:
                raise e

    def obter_perfis_seguidos(self):
        self.login()
        self.log("Buscando perfis seguidos...")
        try:
            following = self.client.user_following(self.client.user_id)
            return [user.username for user in following.values()]
        except (RateLimitError, ClientThrottledError):
            self.log("Rate Limit atingido ao buscar seguidos. Aguardando 5 minutos.")
            time.sleep(300)
            return []

    def coletar_comentarios_perfil(self, username, posts_limit=1, comments_per_post=50, pausa_post=30):
        self.log(f"🐦 Coletando @{username}...")
        tentativas_perfil = 0
        max_tentativas = 2
        medias = []
        while tentativas_perfil < max_tentativas:
            try:
                user_id = self.client.user_id_from_username(username)
                medias = self.client.user_medias(user_id, amount=posts_limit)
                break
            except (RateLimitError, ClientThrottledError, requests.exceptions.RetryError) as e:
                tentativas_perfil += 1
                self.log(f"⚠️ Rate limit/429 em @{username}. Pausa de 5min. Tentativa {tentativas_perfil}/{max_tentativas}.")
                time.sleep(300)
            except Exception as e:
                self.log(f"❌ Erro ao carregar posts de @{username}: {e}")
                return pd.DataFrame()
        if not medias:
            self.log(f"⚠️ Nenhum post encontrado para @{username}.")
            return pd.DataFrame()
        
        todos = []
        for idx, media in enumerate(medias, 1):
            try:
                code = media.code
                url = f"https://www.instagram.com/p/{code}/"
                comentarios = self.client.media_comments(media.id, amount=comments_per_post)
                for c in comentarios:
                    todos.append({
                        "candidato": username,
                        "texto": c.text,
                        "autor_username": c.user.username,
                        "timestamp": c.timestamp,
                        "post_url": url,
                        "post_caption": media.caption_text or "",
                        "likes_comentario": c.like_count
                    })
                self.log(f"    ✓ {len(comentarios)} comentários do post {code}")
                if idx < len(medias):
                    self.log(f"    ⏳ Aguardando {pausa_post}s antes do próximo post...")
                    time.sleep(pausa_post)
            except Exception as e:
                self.log(f"    ❌ Erro no post {code}: {e}")
                continue
        self.log(f"  📦 Total de comentários de @{username}: {len(todos)}")
        return pd.DataFrame(todos)

    def coletar_todos_seguidos(self, posts_por_perfil=1, limite_perfis=1, pausa_entre_perfis=180, comments_por_post=50):
        perfis = self.obter_perfis_seguidos()
        if limite_perfis:
            perfis = perfis[:limite_perfis]
        self.log(f"\n📋 Serão processados {len(perfis)} perfis, {posts_por_perfil} post(s) cada, pausa de {pausa_entre_perfis}s entre perfis.\n")
        
        todos_dfs = []
        for i, perfil in enumerate(perfis, 1):
            self.log(f"\n=== Coletando {i}/{len(perfis)}: @{perfil} ===")
            df = self.coletar_comentarios_perfil(perfil, posts_limit=posts_por_perfil, comments_per_post=comments_por_post)
            if not df.empty:
                todos_dfs.append(df)
            if i < len(perfis):
                self.log(f"⏳ Aguardando {pausa_entre_perfis}s antes do próximo perfil...")
                time.sleep(pausa_entre_perfis)
        
        if todos_dfs:
            df_final = pd.concat(todos_dfs, ignore_index=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome = f"dados_brutos_{timestamp}.csv"
            df_final.to_csv(nome, index=False, encoding="utf-8-sig")
            self.log(f"\n💾 Dados salvos em {nome} ({len(df_final)} comentários)")
            return df_final
        return pd.DataFrame()