# coletor_apify.py
import os
import time
import json
from apify_client import ApifyClient
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

class ColetorApify:
    def __init__(self):
        self.client = ApifyClient(os.getenv("APIFY_API_TOKEN"))
        self.master_username = "monitoramento.discurso"
        self.perfis_file_json = "perfis_monitorados.json"
        self.perfis_file_csv = "validacao_perfis.csv"
    
    def carregar_perfis_prioritarios(self, limite=10):
        """Carrega perfis (priorizando a planilha de validação) e seleciona balanceado"""
        if os.path.exists(self.perfis_file_csv):
            print(f"✅ Usando planilha de validação: {self.perfis_file_csv}")
            df_perfis = pd.read_csv(self.perfis_file_csv)
            perfis = df_perfis.to_dict("records")
        elif os.path.exists(self.perfis_file_json):
            print(f"⚠️ Planilha de validação não encontrada. Usando JSON original.")
            with open(self.perfis_file_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            perfis = data.get("perfis_detalhes", [])
        else:
            print("❌ Nenhum arquivo de perfis encontrado.")
            return []
            
        # Seleção balanceada para teste com base na planilha validada
        nacionais = [p for p in perfis if p["categoria"] == "nacional"][:5]
        estaduais = [p for p in perfis if p["categoria"] == "estadual_local"][:5]
        
        selecionados = nacionais + estaduais
        return selecionados[:limite]

    def obter_seguidos(self):
        """Retorna lista de usernames seguidos pela conta mestre"""
        run_input = {
            "username": [self.master_username],
            "resultsType": "following",
            "resultsLimit": 500,
            "searchLimit": 1,
            "proxy": {"useApifyProxy": True}
        }
        run = self.client.actor("apify/instagram-scraper").call(run_input=run_input)
        items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
        usernames = [item["username"] for item in items if "username" in item]
        return usernames
    
    def coletar_posts(self, usernames, posts_por_perfil=3):
        """Coleta últimos posts de uma lista de perfis"""
        posts = []
        for username in usernames:
            print(f"📸 Coletando posts de @{username}...")
            try:
                run_input = {
                    "username": [username],
                    "resultsType": "posts",
                    "resultsLimit": posts_por_perfil,
                    "searchLimit": 1,
                    "proxy": {"useApifyProxy": True}
                }
                run = self.client.actor("apify/instagram-scraper").call(run_input=run_input)
                items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
                for item in items:
                    posts.append({
                        "username": username,
                        "post_url": f"https://instagram.com/p/{item['shortcode']}",
                        "shortcode": item["shortcode"],
                        "timestamp": item["timestamp"],
                        "caption": item.get("caption", ""),
                        "likes": item.get("likesCount", 0)
                    })
                time.sleep(2)
            except Exception as e:
                print(f"⚠️ Erro coletando posts de @{username}: {str(e)}")
                continue
        return posts
    
    def coletar_comentarios(self, posts, comentarios_por_post=10):
        """Coleta comentários de uma lista de posts"""
        comentarios = []
        for post in posts:
            print(f"💬 Coletando comentários do post {post['shortcode']} (@{post['username']})...")
            try:
                run_input = {
                    "shortcode": [post["shortcode"]],
                    "resultsType": "comments",
                    "resultsLimit": comentarios_por_post,
                    "proxy": {"useApifyProxy": True}
                }
                run = self.client.actor("apify/instagram-scraper").call(run_input=run_input)
                items = list(self.client.dataset(run["defaultDatasetId"]).iterate_items())
                for item in items:
                    comentarios.append({
                        "candidato": post["username"],
                        "texto": item.get("text", ""),
                        "autor_username": item.get("ownerUsername", ""),
                        "timestamp": item.get("timestamp", ""),
                        "post_url": post["post_url"],
                        "likes_comentario": item.get("likesCount", 0)
                    })
                time.sleep(1)
            except Exception as e:
                print(f"⚠️ Erro coletando comentários do post {post['shortcode']}: {str(e)}")
                continue
        return comentarios
    
    def pipeline_teste_balanceado(self, limite=10, posts_por_perfil=2, comentarios_por_post=10):
        print(f"🎯 Iniciando TESTE BALANCEADO com {limite} perfis...")
        
        perfis_info = self.carregar_perfis_prioritarios(limite)
        usernames = [p["username"] for p in perfis_info]
        
        print(f"📋 Perfis selecionados para raspagem: {', '.join(usernames)}")
        
        posts = self.coletar_posts(usernames, posts_por_perfil)
        print(f"✅ {len(posts)} posts coletados.")
        
        comentarios = self.coletar_comentarios(posts, comentarios_por_post)
        
        # Merge com as categorias validadas para o CSV final
        df_comentarios = pd.DataFrame(comentarios)
        df_perfis = pd.DataFrame(perfis_info)
        
        if not df_comentarios.empty:
            df_final = df_comentarios.merge(df_perfis, left_on="candidato", right_on="username", how="left")
            df_final.to_csv("dados_brutos_apify_teste.csv", index=False, encoding="utf-8-sig")
            print(f"✅ TESTE CONCLUÍDO. {len(df_final)} comentários salvos em dados_brutos_apify_teste.csv")
            return df_final
        else:
            print("❌ Nenhum comentário coletado no teste.")
            return pd.DataFrame()

if __name__ == "__main__":
    coletor = ColetorApify()
    # Executa o teste de 10 perfis balanceados conforme a validação
    coletor.pipeline_teste_balanceado(limite=10, posts_por_perfil=2, comentarios_por_post=10)
