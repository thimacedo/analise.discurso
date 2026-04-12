import os
import time
import random
import pandas as pd
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientThrottledError
from dotenv import load_dotenv

load_dotenv()

class ColetorSeguro:
    def __init__(self, session_file="session.json"):
        self.client = Client()
        self.session_file = session_file
        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError("IG_USERNAME ou IG_PASSWORD não configurados no .env")

    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Coletor] {msg}")

    def login(self):
        """Autenticação com persistência de sessão para evitar bloqueios"""
        if os.path.exists(self.session_file):
            try:
                self.client.load_settings(self.session_file)
                self.client.get_timeline_feed()
                self.log("Sessão carregada com sucesso.")
                return
            except Exception:
                self.log("Sessão expirada. Tentando novo login...")

        try:
            self.client.login(self.username, self.password)
            self.client.dump_settings(self.session_file)
            self.log("Novo login realizado e sessão salva.")
        except Exception as e:
            if "Two-factor authentication required" in str(e):
                code = input("⚠️ Digite o código de 2FA: ")
                self.client.login(self.username, self.password, verification_code=code)
                self.client.dump_settings(self.session_file)
                self.log("Login com 2FA realizado.")
            else:
                raise e

    def coletar_comentarios_candidato(self, username_candidato, posts_limit=5, comments_per_post=100):
        """Coleta comentários com rate limiting granular"""
        try:
            user_id = self.client.user_id_from_username(username_candidato)
            medias = self.client.user_medias(user_id, amount=posts_limit)
        except Exception as e:
            self.log(f"Erro ao acessar perfil @{username_candidato}: {e}")
            return pd.DataFrame()

        todos_comentarios = []
        for idx, media in enumerate(medias, 1):
            try:
                self.log(f"  ({idx}/{posts_limit}) Coletando post {media.code}...")
                comentarios = self.client.media_comments(media.id, amount=comments_per_post)
                
                for c in comentarios:
                    todos_comentarios.append({
                        "candidato": username_candidato,
                        "texto": c.text,
                        "autor": c.user.username,
                        "timestamp": c.created_at_utc,
                        "post_url": f"https://www.instagram.com/p/{media.code}/",
                        "post_obs": media.caption_text[:100] if media.caption_text else ""
                    })
                
                # Pausa aleatória entre posts para simular comportamento humano
                time.sleep(random.uniform(2, 5))
                
            except ClientThrottledError:
                self.log("Rate limit atingido. Aguardando 120 segundos...")
                time.sleep(120)
            except Exception as e:
                self.log(f"Erro no post {media.code}: {e}")
                continue

        return pd.DataFrame(todos_comentarios)

    def coletar_multiplos_candidatos(self, lista_candidatos, posts_por_candidato=5):
        self.login()
        todas_as_dfs = []
        
        for i, candidato in enumerate(lista_candidatos, 1):
            self.log(f"--- Iniciando Candidato {i}/{len(lista_candidatos)}: @{candidato} ---")
            df_cand = self.coletar_comentarios_candidato(candidato, posts_limit=posts_por_candidato)
            
            if not df_cand.empty:
                todas_as_dfs.append(df_cand)
            
            if i < len(lista_candidatos):
                pausa = random.uniform(15, 30)
                self.log(f"Aguardando {pausa:.1f}s antes do próximo perfil...")
                time.sleep(pausa)

        if todas_as_dfs:
            df_final = pd.concat(todas_as_dfs, ignore_index=True)
            filename = f"dados_brutos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_final.to_csv(filename, index=False, encoding="utf-8-sig")
            self.log(f"Coleta concluída! {len(df_final)} registros salvos em {filename}")
            return df_final
        
        return pd.DataFrame()
