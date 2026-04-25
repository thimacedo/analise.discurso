import httpx
import time
import json
import os
from textblob import TextBlob
from collections import Counter
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)
nltk.download('punkt_tab', quiet=True)

# --- CONFIGURAÇÕES SEGURAS (Use variáveis de ambiente no Vercel/GitHub) ---
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "d0f8b83ba1msh27e35d3d042e3afp134bb9jsnd112e08fb6b8") # Sua chave aqui para teste local
RAPIDAPI_HOST = "instagram-scrapper-new.p.rapidapi.com"

SUPABASE_URL = os.getenv("SUPABASE_URL", "SUA_URL_DO_SUPABASE")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "SUA_SERVICE_ROLE_KEY")

# Clientes HTTP
supabase = httpx.Client(
    base_url=f"{SUPABASE_URL}/rest/v1",
    headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
)

rapidapi = httpx.Client(
    headers={
        "Content-Type": "application/json",
        "x-rapidapi-host": RAPIDAPI_HOST,
        "x-rapidapi-key": RAPIDAPI_KEY
    }
)

# --- FUNÇÕES DE NLP ---
def process_text(comments_list):
    stop_words = set(stopwords.words('portuguese'))
    all_words = []
    sentiments = {"Positivo": 0, "Neutro": 0, "Negativo": 0}
    for comment in comments_list:
        polarity = TextBlob(comment).sentiment.polarity
        if polarity > 0.1: sentiments["Positivo"] += 1
        elif polarity < -0.1: sentiments["Negativo"] += 1
        else: sentiments["Neutro"] += 1
        words = nltk.word_tokenize(comment.lower(), language='portuguese')
        words = [w for w in words if w.isalpha() and w not in stop_words]
        all_words.extend(words)
    return Counter(all_words).most_common(10), sentiments

# --- FUNÇÕES DE BANCO ---
def upsert_candidato(data):
    try:
        supabase.post(f"/candidatos?on_conflict=username", json=[data], headers={"Prefer": "return=representation, resolution=merge-duplicates"})
        print(f"  [DB] Perfil {data['username']} salvo.")
    except Exception as e:
        print(f"  [DB ERRO] Perfil: {e}")

def insert_comentarios(comments_data):
    if not comments_data: return
    try:
        supabase.post(f"/comentarios?on_conflict=id_externo", json=comments_data, headers={"Prefer": "return=representation, resolution=merge-duplicates"})
        print(f"  [DB] {len(comments_data)} comentários salvos.")
    except Exception as e:
        print(f"  [DB ERRO] Comentários: {e}")

# --- FUNÇÕES RAPIDAPI ---
def get_user_feed(username):
    """Busca os últimos posts de um perfil via RapidAPI"""
    # NOTA: Verifique na documentação da sua API no RapidAPI qual é o endpoint exato para feed de usuário.
    # Geralmente é algo como /getFeedByUsername ou /getUserMedias
    url = f"https://{RAPIDAPI_HOST}/getFeedByUsername" # AJUSTE ESTA ROTA CONFORME A DOCUMENTAÇÃO
    payload = { "username": username }
    
    try:
        response = rapidapi.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        # A estrutura exata depende da API. Aqui assumimos que retorna uma lista de posts.
        # Pode ser data['data'], data['items'], etc.
        return data.get('data', [])[:3] # Retorna os 3 primeiros posts
    except Exception as e:
        print(f"  [API ERRO] Buscando feed de {username}: {e}")
        return []

def get_comments(post_id):
    """Busca comentários de um post específico via RapidAPI"""
    # NOTA: Verifique na documentação o endpoint de comentários. Geralmente /getMediaComments
    url = f"https://{RAPIDAPI_HOST}/getMediaComments" # AJUSTE ESTA ROTA CONFORME A DOCUMENTAÇÃO
    payload = { "media_id": post_id }
    
    try:
        response = rapidapi.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get('comments', [])[:30] # Limita a 30 comentários
    except Exception as e:
        # print(f"  [API ERRO] Buscando comentários do post {post_id}: {e}")
        return []

def get_feed_by_hashtag(tag):
    """Função bônus: Usa exatamente o endpoint que você mandou"""
    url = f"https://{RAPIDAPI_HOST}/getFeedByHashtagLegacy"
    payload = { "tag": tag } # Geralmente exige o nome da tag no payload
    
    try:
        response = rapidapi.post(url, json=payload)
        response.raise_for_status()
        return response.json().get('data', [])
    except Exception as e:
        print(f"  [API ERRO] Hashtag #{tag}: {e}")
        return []

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    print("Buscando alvos no Supabase...")
    response = supabase.get("/candidatos?status_monitoramento=eq.ATIVO&order=atualizado_em.asc&limit=10")
    target_profiles = response.json()
    
    if not target_profiles:
        print("Nenhum perfil ativo.")
        exit()

    all_comments_text = []

    for profile in target_profiles:
        username = profile['username']
        print(f"\n--- Raspando @{username} via RapidAPI ---")
        
        # 1. Atualiza dados do candidato (se a API prover info do user, você pode puxar aqui)
        upsert_candidato({
            "username": username,
            "atualizado_em": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })

        # 2. Busca os posts
        posts = get_user_feed(username)
        
        comments_to_db = []
        for post in posts:
            post_id = post.get('id') # ou 'pk', dependendo do retorno da API
            if not post_id: continue
            
            print(f"  -> Extraindo comentários do post {post_id}...")
            comments = get_comments(post_id)
            
            for comment in comments:
                # Mapeamento: Ajuste os nomes dos campos (comment['text'], comment['user']['username']) conforme o JSON que a API retornar
                comment_data = {
                    "id_externo": comment.get('id'),
                    "candidato_id": username,
                    "post_id": post_id,
                    "autor_username": comment.get('owner', {}).get('username'), 
                    "texto_bruto": comment.get('text'),
                    "data_publicacao": comment.get('created_at'),
                    "likes": comment.get('likes_count', 0),
                    "processado_ia": False
                }
                comments_to_db.append(comment_data)
                if comment.get('text'):
                    all_comments_text.append(comment.get('text'))
            
            time.sleep(1) # Pausa de 1s (Apenas para não estourar rate limit da API, se houver)

        # 3. Salva no Supabase
        insert_comentarios(comments_to_db)

    # Geração de relatório local
    if all_comments_text:
        word_freq, sentiments = process_text(all_comments_text)
        with open("relatorio_api.md", "w", encoding="utf-8") as f:
            f.write("# 📊 Relatório via API\n\n")
            f.write("## 🎭 Sentimento\n")
            for k, v in sentiments.items(): f.write(f"- **{k}**: {v}\n")
            f.write("\n## 📈 Top 10 Palavras\n")
            for word, count in word_freq: f.write(f"1. **{word}**: {count}\n")
        print("\nRelatório gerado!")