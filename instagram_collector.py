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
            print(f"🔐 Iniciando novo login para @{user}...")
            try:
                self.client.login(user, pw)
                self._save_session()
                print("✅ Novo login realizado e sessão salva.")
            except Exception as e:
                if "Two-factor authentication required" in str(e):
                    code = input("⚠️ 2FA detectado. Digite o código enviado: ")
                    self.client.login(user, pw, verification_code=code)
                    self._save_session()
                    print("✅ Login com 2FA realizado e sessão salva.")
                else:
                    print(f"❌ Erro na autenticação: {e}")
                    raise
        else:
            print(f"♻️ Sessão reutilizada para @{user}")

    def _load_session(self):
        if os.path.exists(self.session_file):
            try:
                self.client.load_settings(self.session_file)
                print(f"📂 Configurações de sessão carregadas de {self.session_file}")
            except Exception as e:
                print(f"⚠️ Erro ao carregar sessão: {e}")

    def _save_session(self):
        try:
            self.client.dump_settings(self.session_file)
            print(f"💾 Sessão persistida em {self.session_file}")
        except Exception as e:
            print(f"⚠️ Erro ao salvar sessão: {e}")

    def _is_logged_in(self):
        try:
            return self.client.get_timeline_feed()
        except:
            return False
    
    def collect_candidate_comments(self, candidate_username, posts_limit=10, comments_per_post=200):
        """
        Coleta comentários de posts de um candidato específico.
        """
        try:
            print(f"  📥 Buscando ID de @{candidate_username}...")
            user_id = self.client.user_id_from_username(candidate_username)
            print(f"  📥 Coletando {posts_limit} posts mais recentes...")
            medias = self.client.user_medias(user_id, amount=posts_limit)
            
            all_comments = []
            for media in medias:
                print(f"    💬 Extraindo comentários do post {media.code}...")
                comments = self.client.media_comments(media.id, amount=comments_per_post)
                for comment in comments:
                    all_comments.append({
                        'candidate': candidate_username,
                        'text': comment.text,
                        'username': comment.user.username,
                        'timestamp': comment.timestamp,
                        'post_url': f"https://instagram.com/p/{media.code}",
                        'post_caption': media.caption_text if media.caption_text else '',
                        'likes_count': comment.like_count
                    })
                time.sleep(2)  # Cooldown para evitar rate limiting (Shadowban)
            return pd.DataFrame(all_comments)
        except Exception as e:
            print(f"  ⚠️ Erro ao coletar @{candidate_username}: {e}")
            return pd.DataFrame()
    
    def monitor_multiple_candidates(self, candidates_list, posts_per_candidate=15):
        """
        Executa a monitoria em lote para uma lista de candidatos.
        """
        all_dfs = []
        for cand in candidates_list:
            print(f"\n🚀 Iniciando coleta em @{cand}...")
            df = self.collect_candidate_comments(cand, posts_limit=posts_per_candidate)
            if not df.empty:
                all_dfs.append(df)
                print(f"  ✓ {len(df)} comentários processados para @{cand}.")
            else:
                print(f"  ! Nenhum dado extraído para @{cand}.")
        
        if not all_dfs:
            return pd.DataFrame()
            
        final_df = pd.concat(all_dfs, ignore_index=True)
        final_df.to_csv('dados_brutos.csv', index=False, encoding='utf-8')
        print(f"\n💾 Arquivo 'dados_brutos.csv' gerado com {len(final_df)} registros.")
        return final_df