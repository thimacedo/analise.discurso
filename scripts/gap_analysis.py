import os
import json
import requests

# Configurações do Supabase
SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def get_db_status():
    profiles_path = "data/perfis_monitorados.json"
    with open(profiles_path, "r", encoding="utf-8") as f:
        perfis_desejados = json.load(f)
    
    # Pegar todos os dados de candidatos
    url = f"{SUPABASE_URL}/rest/v1/candidatos"
    response = requests.get(url, headers=HEADERS)
    db_data = response.json() if response.status_code == 200 else []
    db_map = {p['username']: p for p in db_data}
    
    status_report = []
    print(f"📊 Analisando {len(perfis_desejados)} perfis...")
    
    for perfil in perfis_desejados:
        username = perfil['username']
        db_record = db_map.get(username)
        
        in_db = db_record is not None
        posts = db_record.get('posts_avaliados_count', 0) if in_db else 0
        comms = db_record.get('comentarios_totais_count', 0) if in_db else 0
        
        status_report.append({
            "username": username,
            "full_name": perfil.get("full_name", ""),
            "in_db": in_db,
            "posts": posts,
            "comments": comms,
            "cargo": db_record.get('cargo') if in_db else None
        })

    # Salvar
    with open("data/gap_analysis_report.json", "w", encoding="utf-8") as f:
        json.dump(status_report, f, indent=4, ensure_ascii=False)
    
    missing = [p['username'] for p in status_report if not p['in_db']]
    low_data = [p['username'] for p in status_report if p['in_db'] and (p['posts'] or 0) < 5]
    
    print(f"\n✅ Relatório concluído.")
    print(f"❌ Ausentes no DB: {len(missing)}")
    print(f"⚠️ Poucos dados (<5 posts): {len(low_data)}")
    
    if missing:
        print(f"Primeiros ausentes: {', '.join(missing[:10])}")

if __name__ == "__main__":
    get_db_status()
