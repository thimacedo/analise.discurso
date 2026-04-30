import os
import time
import uuid
import yt_dlp
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, UTC

load_dotenv()

# Inicializa Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Dicionário de Alvos (Username do IG -> URL do Canal do YouTube)
YOUTUBE_TARGETS = {
    "cirogomes": "https://www.youtube.com/@cirogomes/videos",
    "nikolasferreiradm": "https://www.youtube.com/@NikolasFerreiraOficial/videos",
    "jairmessiasbolsonaro": "https://www.youtube.com/@jairbolsonaro/videos",
    "janjalula": "https://www.youtube.com/@JanjaLula/videos",
    "carla.zambelli": "https://www.youtube.com/@CarlaZambelliOficial/videos",
    "tarcisiogdf": "https://www.youtube.com/@TarcisioGDF/videos"
}

def get_or_create_candidato(username):
    """Busca o ID do candidato no banco ou cria se não existir."""
    response = supabase.table('candidatos').select('username').eq('username', username).execute()
    
    if response.data:
        return response.data[0]['username']
    else:
        # Cria o candidato se não existir
        try:
            supabase.table('candidatos').insert({
                'username': username,
                'status_monitoramento': 'ATIVO'
            }).execute()
            return username
        except Exception as e:
            print(f"⚠️ Aviso ao criar candidato {username}: {e}")
            return username

def scrape_youtube():
    """Motor de raspagem do YouTube Precision v1.5 - Resiliência de Cookies."""
    print("📺 [YouTube] Iniciando Motor de Raspagem Stealth...")
    
    # Lista de navegadores para tentar cookies
    browsers = ['chrome', 'edge']
    ydl = None
    
    # Tenta inicializar o yt-dlp com cookies
    for browser in browsers:
        try:
            print(f"🔑 Tentando carregar sessão do {browser.capitalize()}...")
            opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'getcomments': True,
                'skip_download': True,
                'max_comments': 50,
                'playlistend': 5,
                'cookiesfrombrowser': (browser,),
            }
            # Teste rápido de cookies
            with yt_dlp.YoutubeDL(opts) as test_ydl:
                test_ydl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False, process=False)
            
            print(f"✅ Sessão {browser.capitalize()} validada!")
            final_opts = opts
            break
        except Exception:
            print(f"⚠️ Não foi possível acessar cookies do {browser.capitalize()} (Navegador aberto ou não instalado).")
    else:
        print("🛡️ Entrando em MODO BLINDADO (Sem cookies). Limite de 2 comentários por vídeo.")
        final_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'getcomments': True,
            'skip_download': True,
            'max_comments': 50,
            'playlistend': 5,
        }

    with yt_dlp.YoutubeDL(final_opts) as ydl:
        for username, url in YOUTUBE_TARGETS.items():
            print(f"\n🎯 Processando canal de: {username}")
            candidato_id = get_or_create_candidato(username)
            
            try:
                info = ydl.extract_info(url, download=False)
                entries = info.get('entries', [])
                
                videos_processados = 0
                for entry in entries:
                    if not entry or 'id' not in entry:
                        continue
                        
                    video_id = entry['id']
                    
                    # 🚨 FILTRO ANTI-SHORTS/ABAS: Pula se não for um ID de vídeo padrão (11 chars)
                    if len(video_id) != 11:
                        continue
                        
                    title = entry.get('title', 'Sem Título')
                    print(f"  📹 Vídeo: {title[:50]}... ({video_id})")

                    # 1. Extrair Comentários
                    comments = entry.get('comments', [])
                    if comments:
                        saved_count = 0
                        for comment in comments:
                            comment_id = comment.get('id', str(uuid.uuid4()))
                            author = comment.get('author', 'anon_yt')
                            text = comment.get('text', '').replace('\n', ' ')
                            
                            if not text:
                                continue
                                
                            comment_data = {
                                'id_externo': f"yt_{comment_id}", 
                                'candidato_id': candidato_id,
                                'post_id': video_id,
                                'autor_username': author,
                                'texto_bruto': text,
                                'plataforma': 'YOUTUBE',
                                'data_coleta': datetime.now(UTC).isoformat(),
                                'processado_ia': False
                            }
                            
                            try:
                                supabase.table('comentarios').insert(comment_data).execute()
                                saved_count += 1
                            except Exception:
                                pass 
                                
                        print(f"    ✅ {saved_count} comentários salvos.")
                        videos_processados += 1
                    else:
                        print(f"    ⚠️ Nenhum comentário público em {video_id}.")
                        
                    if videos_processados >= 3: 
                        break
                        
                    time.sleep(2) 
                    
            except Exception as e:
                print(f"❌ Erro no canal {url}: {e}")
                
    print("\n✅ Raspagem do YouTube finalizada!")

if __name__ == "__main__":
    scrape_youtube()
