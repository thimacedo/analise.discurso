
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, time, yt_dlp, uuid
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
supa = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

res = supa.table('candidatos').select('id, username, nome_completo').is_('last_scraped_at', 'null').limit(20).execute()
targets = res.data
ydl_opts = {
    'quiet': True, 
    'extract_flat': False, 
    'getcomments': True, 
    'skip_download': True, 
    'max_comments': 30, 
    'playlistend': 2,
    'cookiefile': 'cookies.txt',
    'extractor_args': {'youtube': {'player_client': ['web']}}
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    for t in targets:
        q = f"ytsearch1:{t['nome_completo'] or t['username']} política"
        print(f"🔍 {q}")
        try:
            info = ydl.extract_info(q, download=False)
            entries = info.get('entries', [info])
            for e in entries:
                if not e or len(e.get('id', '')) != 11: continue
                for c in e.get('comments', []):
                    data = {
                        "id_externo": f"yt_{c.get('id', uuid.uuid4())}",
                        "candidato_id": t['username'],
                        "post_id": e['id'],
                        "autor_username": c.get('author', 'anon'),
                        "texto_bruto": c.get('text', ''),
                        "plataforma": "YOUTUBE",
                        "data_coleta": datetime.utcnow().isoformat(),
                        "processado_ia": False
                    }
                    try: supa.table('comentarios').upsert(data, on_conflict='id_externo').execute()
                    except: pass
            supa.table('candidatos').update({'last_scraped_at': datetime.utcnow().isoformat()}).eq('id', t['id']).execute()
            print(f"✅ {t['username']}")
            time.sleep(3)
        except Exception as ex: print(f"❌ {t['username']}: {ex}")

print("Fim.")
