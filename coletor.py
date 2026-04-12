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
    def __init__(self, username=None, password=None, session_file="session.json"):
        self.client = Client()
        self.session_file = session_file
        self.username = username or os.getenv("IG_USERNAME")
        self.password = password or os.getenv("IG_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError("IG_USERNAME ou IG_PASSWORD não configurados. Use .env ou variáveis de ambiente.")

    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Coletor] {msg}")

    def login(self):
        """Autenticação com persistência de sessão para evitar bloqueios"""
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
        """Retorna lista de usernames dos perfis que a conta está seguindo"""
        self.login()
        user_id = self.client.user_id
        following = self.client.user_following(user_id)
        return [user.username for user in following.values()]

    def coletar_comentarios_perfil(self, username, posts_limit=10, comments_per_post=200, tentativa=1):
        """Coleta comentários de um perfil com retry e backoff exponencial em caso de 429."""
        self.log(f"🐦 Coletando @{username} (tentativa {tentativa})...")
        
        # Backoff exponencial ANTES de tentar novamente após erro 429
        if tentativa > 1:
            wait = 60 * (2 ** (tentativa - 1))  # 60s, 120s, 240s, 480s...
            self.log(f"⏳ Aguardando {wait}s antes de tentar novamente...")
            time.sleep(wait)
        
        try:
            user_id = self.client.user_id_from_username(username)
        except Exception as e:
            self.log(f"❌ Usuário {username} não encontrado: {e}")
            return pd.DataFrame()
        
        try:
            medias = self.client.user_medias(user_id, amount=posts_limit)
        except ClientThrottledError as e:
            if tentativa <= 3:
                self.log(f"⚠️ Rate limit (429) em @{username}. Tentativa {tentativa} de 3.")
                return self.coletar_comentarios_perfil(username, posts_limit, comments_per_post, tentativa + 1)
            else:
                self.log(f"❌ Falha após 3 tentativas para @{username}. Pulando perfil.")
                return pd.DataFrame()
        except Exception as e:
            self.log(f"❌ Erro ao carregar posts de @{username}: {e}")
            return pd.DataFrame()
        
        todos = []
        for media in medias:
            try:
                code = media.code
                url = f"https://www.instagram.com/p/{code}/"
                comentarios = self.client.media_comments(media.id, amount=comments_per_post)
                
                for c in comentarios:
                    todos.append({
                        "candidato": username,
                        "texto": c.text,
                        "autor_username": c.user.username,
                        "timestamp": c.created_at_utc,
                        "post_url": url,
                        "post_caption": media.caption_text if media.caption_text else "",
                        "likes_comentario": c.like_count
                    })
                
                self.log(f"    ✓ {len(comentarios)} comentários do post {code}")
                # Pausa entre posts (2 a 6 segundos)
                time.sleep(random.uniform(2, 6))
                
            except ClientThrottledError:
                self.log(f"    ⚠️ Rate limit no post {code}. Aguardando 45s...")
                time.sleep(45)
            except Exception as e:
                self.log(f"    ❌ Erro no post {code}: {e}")
                continue
        
        return pd.DataFrame(todos)

    def coletar_todos_seguidos(self, posts_por_perfil=10, limite_perfis=None):
        """Coleta comentários de todos os perfis seguidos, com limite opcional para teste."""
        perfis = self.obter_perfis_seguidos()
        
        if limite_perfis:
            perfis = perfis[:limite_perfis]
            self.log(f"\n📋 MODO TESTE: Apenas {len(perfis)} perfis serão processados.\n")
        else:
            self.log(f"\n📋 {len(perfis)} perfis serão processados.\n")
        
        todos_dfs = []
        for i, perfil in enumerate(perfis, 1):
            self.log(f"\n=== Coletando {i}/{len(perfis)}: @{perfil} ===")
            
            df = self.coletar_comentarios_perfil(perfil, posts_limit=posts_por_perfil)
            if not df.empty:
                todos_dfs.append(df)
            
            # Pausa GRANDE entre perfis para evitar bloqueio (30 a 60 segundos)
            if i < len(perfis):
                pausa = random.uniform(30, 60)
                self.log(f"⏳ Aguardando {pausa:.1f}s antes do próximo perfil...")
                time.sleep(pausa)
        
        if todos_dfs:
            df_final = pd.concat(todos_dfs, ignore_index=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome = f"dados_brutos_{timestamp}.csv"
            df_final.to_csv(nome, index=False, encoding="utf-8-sig")
            self.log(f"\n💾 Dados salvos em {nome} ({len(df_final)} comentários)")
            return df_final
        else:
            self.log("❌ Nenhum dado coletado.")
            return pd.DataFrame()

    # Mantém método antigo para compatibilidade
    def coletar_comentarios_candidato(self, username_candidato, posts_limit=5, comments_per_post=100):
        return self.coletar_comentarios_perfil(username_candidato, posts_limit, comments_per_post)
    
    # Mantém método antigo para compatibilidade
    def coletar_multiplos_candidatos(self, lista_candidatos, posts_por_candidato=5):
        self.login()
        todas_as_dfs = []
        
        for i, candidato in enumerate(lista_candidatos, 1):
            self.log(f"--- Iniciando Candidato {i}/{len(lista_candidatos)}: @{candidato} ---")
            df_cand = self.coletar_comentarios_perfil(candidato, posts_limit=posts_por_candidato)
            
            if not df_cand.empty:
                todas_as_dfs.append(df_cand)
            
            if i < len(lista_candidatos):
                pausa = random.uniform(30, 60)
                self.log(f"Aguardando {pausa:.1f}s antes do próximo perfil...")
                time.sleep(pausa)

        if todas_as_dfs:
            df_final = pd.concat(todas_as_dfs, ignore_index=True)
            filename = f"dados_brutos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df_final.to_csv(filename, index=False, encoding="utf-8-sig")
            self.log(f"Coleta concluída! {len(df_final)} registros salvos em {filename}")
            return df_final
        
        return pd.DataFrame()