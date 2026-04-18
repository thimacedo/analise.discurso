import pandas as pd
from instagrapi import Client
import time
import os
from dotenv import load_dotenv

load_dotenv()

class ForensicCollector:
    def __init__(self, username=None, password=None, session_file="session.json"):
        self.client = Client()
        self.session_file = session_file
        
        user = username or os.getenv('IG_USERNAME')
        pw = password or os.getenv('IG_PASSWORD')
        
        if not user or not pw:
            raise ValueError("Credenciais do Instagram não encontradas no .env (IG_USERNAME/IG_PASSWORD)")
            
        # Tentativa de carregar sessão existente
        self._load_session()
        
        if not self._is_logged_in():
            print(f"Iniciando novo login para @{user}...")
            try:
                self.client.login(user, pw)
                self._save_session()
                print("Novo login realizado e sessao salva.")
            except Exception as e:
                if "Two-factor authentication required" in str(e):
                    # No modo automatizado, o 2FA deve ser evitado ou tratado externamente
                    print("Erro: 2FA detectado. Por favor, logue manualmente uma vez para gerar a sessao.")
                    raise
                else:
                    print(f"Erro na autenticacao: {e}")
                    raise
        else:
            print(f"Sessao reutilizada para @{user}")

    def _load_session(self):
        if os.path.exists(self.session_file):
            try:
                self.client.load_settings(self.session_file)
                print(f"Configuracoes de sessao carregadas de {self.session_file}")
            except Exception as e:
                print(f"Erro ao carregar sessao: {e}")

    def _save_session(self):
        try:
            self.client.dump_settings(self.session_file)
            print(f"Sessao persistida em {self.session_file}")
        except Exception as e:
            print(f"Erro ao salvar sessao: {e}")

    def _is_logged_in(self):
        try:
            return self.client.get_timeline_feed()
        except:
            return False

    def monitor_multiple_candidates(self, user_list, posts_per_candidate=10):
        all_comments = []
        
        for username in user_list:
            print(f"Buscando posts de @{username}...")
            try:
                user_id = self.client.user_id_from_username(username)
                posts = self.client.user_medias(user_id, amount=posts_per_candidate)
                
                print(f"Coletando comentarios de {len(posts)} posts de @{username}...")
                for post in posts:
                    comments = self.client.media_comments(post.id)
                    for comment in comments:
                        all_comments.append({
                            'id': comment.pk,
                            'post_id': post.id,
                            'candidate': username,
                            'owner_username': comment.user.username,
                            'text': comment.text,
                            'timestamp': comment.created_at_utc
                        })
                    print(f"Aguardando 10s para proximo post de @{username}...")
                    time.sleep(10) # Pausa maior entre posts
            except Exception as e:
                print(f"Erro ao monitorar @{username}: {e}")
                print("Aguardando 30s para resfriamento de IP...")
                time.sleep(30) # Resfriamento em caso de erro
                continue
                
        return pd.DataFrame(all_comments)
