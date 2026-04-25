import os
import time
import random
import pandas as pd
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, ClientThrottledError
from dotenv import load_dotenv

load_dotenv()

class ColetorSeguro:
    def __init__(self, session_file="session.json"):
        self.client = Client()
        self.session_file = session_file
        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")
        if not self.username or not self.password:
            raise ValueError("Credenciais não configuradas")

    def login(self):
        if os.path.exists(self.session_file):
            self.client.load_settings(self.session_file)
            try:
                self.client.get_timeline_feed()
                print("✅ Sessão carregada.")
                return
            except (LoginRequired, ChallengeRequired):
                print("⚠️ Sessão expirada. Refazendo login...")
        self.client.login(self.username, self.password)
        self.client.dump_settings(self.session_file)
        print("✅ Login OK. Aguardando 60s para evitar detecção...")
        time.sleep(60)  # pausa longa inicial

    def obter_perfis_seguidos(self):
        self.login()
        user_id = self.client.user_id
        seguindo = self.client.user_following(user_id)
        return [seguido.username for seguido in seguindo]

    def coletar_comentarios_perfil(self, username, posts_limit=3, comments_per_post=200, tentativa=1):
        print(f"🐦 Coletando @{username} (tentativa {tentativa})...")
        if tentativa > 1:
            wait = 60 * (2 ** (tentativa - 1))
            print(f"⏳ Aguardando {wait}s antes de tentar novamente...")
            time.sleep(wait)

        try:
            user_id = self.client.user_id_from_username(username)
        except Exception as e:
            print(f"❌ Usuário {username} não encontrado: {e}")
            return pd.DataFrame()

        try:
            medias = self.client.user_medias(user_id, amount=posts_limit)
        except ClientThrottledError as e:
            if tentativa <= 3:
                return self.coletar_comentarios_perfil(username, posts_limit, comments_per_post, tentativa+1)
            else:
                print(f"❌ Falha após 3 tentativas para @{username}. Pulando.")
                return pd.DataFrame()

        todos = []
        for idx, media in enumerate(medias, 1):
            try:
                code = media.code
                url = f"https://www.instagram.com/p/{code}/"
                print(f"    → Post {idx}/{len(medias)}: {code}")
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
                print(f"        ✓ {len(comentarios)} comentários")
                # Pausa longa entre posts (15-25s)
                time.sleep(random.uniform(15, 25))
            except ClientThrottledError:
                print(f"    ⚠️ Rate limit no post {code}. Aguardando 60s...")
                time.sleep(60)
            except Exception as e:
                print(f"    ❌ Erro no post {code}: {e}")
                continue

        print(f"  📦 Total para @{username}: {len(todos)} comentários")
        return pd.DataFrame(todos)

    def coletar_todos_seguidos(self, posts_por_perfil=3, limite_perfis=None):
        perfis = self.obter_perfis_seguidos()
        if limite_perfis:
            perfis = perfis[:limite_perfis]
        print(f"\n📋 Serão processados {len(perfis)} perfis (MODO SEGURO: {posts_por_perfil} posts/perfil)")
        print("⏱️  Delays: 15-25s entre posts, 60-120s entre perfis.\n")

        todos_dfs = []
        for i, perfil in enumerate(perfis, 1):
            print(f"\n=== Coletando {i}/{len(perfis)}: @{perfil} ===")
            df = self.coletar_comentarios_perfil(perfil, posts_limit=posts_por_perfil)
            if not df.empty:
                todos_dfs.append(df)

            if i < len(perfis):
                pausa_entre = random.uniform(60, 120)
                print(f"⏳ Aguardando {pausa_entre:.1f}s antes do próximo perfil...")
                time.sleep(pausa_entre)

        if todos_dfs:
            df_final = pd.concat(todos_dfs, ignore_index=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome = f"dados_brutos_{timestamp}.csv"
            df_final.to_csv(nome, index=False, encoding="utf-8-sig")
            print(f"\n💾 Dados smonitorados em {nome} ({len(df_final)} comentários)")
            return df_final
        else:
            print("❌ Nenhum dado coletado.")
            return pd.DataFrame()

if __name__ == "__main__":
    coletor = ColetorSeguro()
    # Teste ultraconservador: 2 posts, 2 perfis
    coletor.coletar_todos_seguidos(posts_por_perfil=2, limite_perfis=2)
