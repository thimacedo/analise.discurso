import pandas as pd
import time
import random
import os
import json
from datetime import datetime
from instagrapi import Client

class ColetorPublico:
    def __init__(self):
        self.cl = Client()
        self.cl.delay_range = [2, 5]
        self._configurar_sessao()

    def _configurar_sessao(self):
        # Tenta usar a sessão já criada pelo atualizar_perfis.py
        if os.path.exists("session.json"):
            self.cl.load_settings("session.json")
            self.log("Sessao carregada com sucesso.")
        
        # Se não estiver logado, tenta logar usando o .env
        username = os.getenv("IG_USERNAME")
        password = os.getenv("IG_PASSWORD")
        
        try:
            if username and password:
                self.cl.login(username, password)
                self.cl.dump_settings("session.json")
                self.log(f"Logado como @{username}")
            else:
                self.log("Aviso: Sem credenciais no .env. A coleta pode falhar.")
        except Exception as e:
            self.log(f"Erro ao logar: {e}")

    def log(self, msg):
        # Limpa emojis para o console Windows
        msg_limpa = msg.encode('ascii', 'ignore').decode('ascii')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Coletor] {msg_limpa}")

    def coletar_comentarios_perfil(self, username, posts_limit=2):
        self.log(f"Acessando perfil: @{username}")
        todos = []
        
        try:
            # Busca o ID do usuário pelo username
            user_id = self.cl.user_id_from_username(username)
            # Pega os posts mais recentes
            medias = self.cl.user_medias(user_id, amount=posts_limit)
            
            for media in medias:
                self.log(f"  Lendo post {media.pk}...")
                # Pega os comentários do post
                comments = self.cl.media_comments(media.pk, amount=50)
                
                for comment in comments:
                    todos.append({
                        "candidato": username,
                        "texto": comment.text,
                        "autor": comment.user.username,
                        "data": comment.created_at_utc.isoformat(),
                        "id_post": media.pk,
                        "id_comentario": comment.pk,
                        "likes": comment.like_count
                    })
                
                # Pausa entre posts
                time.sleep(random.uniform(3, 7))
                    
        except Exception as e:
            self.log(f"Erro ao acessar @{username}: {e}")
            
        return pd.DataFrame(todos)

    def coletar_todos(self, arquivo_perfis="perfis_monitorados.json", posts_por_perfil=2):
        if not os.path.exists(arquivo_perfis):
            self.log("Arquivo de perfis nao encontrado.")
            return pd.DataFrame()

        with open(arquivo_perfis, 'r', encoding='utf-8') as f:
            perfis = json.load(f).get("perfis", [])

        self.log(f"Iniciando coleta para {len(perfis)} perfis.")
        todos_dfs = []
        
        for i, perfil in enumerate(perfis, 1):
            self.log(f"=== {i}/{len(perfis)}: @{perfil} ===")
            df = self.coletar_comentarios_perfil(perfil, posts_limit=posts_por_perfil)
            
            if not df.empty:
                todos_dfs.append(df)
                
            if i < len(perfis):
                pausa = random.uniform(10, 20)
                time.sleep(pausa)
                
        if todos_dfs:
            df_final = pd.concat(todos_dfs, ignore_index=True)
            self.log(f"Sucesso: {len(df_final)} comentarios coletados.")
            return df_final
            
        self.log("Nenhum dado coletado.")
        return pd.DataFrame()