import instaloader
import pandas as pd
import time
import random
import json
import os
from datetime import datetime

class ColetorPublico:
    def __init__(self):
        # Inicializa o Instaloader SEM login
        self.L = instaloader.Instaloader(
            download_videos=False,
            download_pictures=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False, # Não salva arquivos de comentário no disco
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern="", # Não cria arquivos txt
            storyitem_metadata_txt_pattern=""
        )
        # User-Agent disfarçado para evitar bloqueios primários
        self.L.context._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        })

    def log(self, msg):
        # Remove emojis ou caracteres não-ascii da mensagem antes de imprimir
        msg_limpa = msg.encode('ascii', 'ignore').decode('ascii')
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Anonimo] {msg_limpa}")

    def coletar_comentarios_perfil(self, username, posts_limit=2):
        self.log(f"🕵️ Acessando perfil público: @{username}")
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
                    # Pega todos os comentários do post público
                    for comment in post.get_comments():
                        todos.append({
                            "candidato": username,
                            "texto": comment.text,
                            "autor_username": comment.owner.username,
                            "timestamp": comment.created_at_utc.isoformat(),
                            "post_url": url,
                            "post_caption": post.caption or "",
                            "likes_comentario": comment.likes_count if hasattr(comment, 'likes_count') else 0
                        })
                    
                    count += 1
                    # Pausa entre posts para proteger o IP
                    time.sleep(random.uniform(5, 10))
                    
                except instaloader.exceptions.ConnectionException as e:
                    if "429" in str(e) or "rate limit" in str(e).lower():
                        self.log("    ⚠️ IP bloqueado temporariamente (429). Conta segura! Pausa de 15min.")
                        time.sleep(900)
                    else:
                        self.log(f"    ❌ Erro de conexão no post: {e}")
                        break
                except Exception as e:
                    self.log(f"    ❌ Erro inesperado no post: {e}")
                    break
                    
        except instaloader.exceptions.ProfileNotExistsException:
            self.log(f"❌ Perfil @{username} não existe ou é privado.")
        except Exception as e:
            self.log(f"❌ Erro ao acessar @{username}: {e}")
            
        return pd.DataFrame(todos)

    def coletar_todos(self, arquivo_perfis="perfis_monitorados.json", posts_por_perfil=2):
        if not os.path.exists(arquivo_perfis):
            self.log("❌ Arquivo de perfis não encontrado. Rode 'python atualizar_perfis.py' primeiro.")
            return pd.DataFrame()

        with open(arquivo_perfis, 'r', encoding='utf-8') as f:
            perfis = json.load(f).get("perfis", [])

        self.log(f"\n📋 Iniciando coleta anônima para {len(perfis)} perfis.\n")
        todos_dfs = []
        
        for i, perfil in enumerate(perfis, 1):
            self.log(f"\n=== Coletando {i}/{len(perfis)}: @{perfil} ===")
            df = self.coletar_comentarios_perfil(perfil, posts_limit=posts_por_perfil)
            
            if not df.empty:
                todos_dfs.append(df)
                
            if i < len(perfis):
                pausa = random.uniform(30, 60) # Pausas maiores para scraping anônimo
                self.log(f"⏳ Aguardando {pausa:.1f}s antes do próximo perfil...")
                time.sleep(pausa)
                
        if todos_dfs:
            df_final = pd.concat(todos_dfs, ignore_index=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome = f"dados_brutos_{timestamp}.csv"
            df_final.to_csv(nome, index=False, encoding="utf-8-sig")
            self.log(f"\n💾 Dados salvos em {nome} ({len(df_final)} comentários)")
            return df_final
            
        self.log("⚠️ Nenhum comentário coletado no total.")
        return pd.DataFrame()