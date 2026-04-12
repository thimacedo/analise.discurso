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
    
    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Coletor] {msg}")

    def login(self):
        if os.path.exists(self.session_file):
            try:
                self.client.load_settings(self.session_file)
                self.client.get_timeline_feed()
                self.log("✅ Sessão carregada.")
                return
            except Exception:
                self.log("⚠️ Sessão expirada.")

        self.client.login(self.username, self.password)
        self.client.dump_settings(self.session_file)
        self.log("✅ Login realizado.")
    
    def obter_perfis_seguidos(self):
        self.login()
        self.log("Buscando perfis seguidos...")
        seguindo = self.client.user_following(self.client.user_id)
        return [s.username for s in seguindo.values()]
    
    def coletar_comentarios_perfil(self, username, posts_limit=5):
        self.log(f"Iniciando @{username}")
        try:
            user_id = self.client.user_id_from_username(username)
            medias = self.client.user_medias(user_id, amount=posts_limit)
        except Exception as e:
            self.log(f"Erro no perfil {username}: {e}")
            return []
        
        todos = []
        for media in medias:
            try:
                comentarios = self.client.media_comments(media.id, amount=100)
                for c in comentarios:
                    todos.append({
                        "candidato": username,
                        "texto": c.text,
                        "timestamp": c.created_at_utc,
                        "post_url": f"https://instagram.com/p/{media.code}/"
                    })
                time.sleep(random.uniform(2, 4))
            except Exception: continue
        return todos

    def coletar_todos_seguidos(self, posts_por_perfil=3):
        perfis = self.obter_perfis_seguidos()
        self.log(f"Monitorando {len(perfis)} perfis.")
        
        todos_dados = []
        for perfil in perfis:
            dados = self.coletar_comentarios_perfil(perfil, posts_limit=posts_por_perfil)
            todos_dados.extend(dados)
            time.sleep(random.uniform(10, 15))
        
        if todos_dados:
            df = pd.DataFrame(todos_dados)
            filename = f"dados_brutos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            return df, filename
        return pd.DataFrame(), None
