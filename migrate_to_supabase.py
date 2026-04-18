import sqlite3
import os
import httpx
from datetime import datetime

# CONFIGURAÇÕES SUPABASE (UNIFICADO)
SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
# Usando SERVICE ROLE para ignorar RLS durante a migração inicial
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY"

def migrate_to_supabase_v2():
    print("🚀 Iniciando migração PROFISSIONAL para o Supabase...")
    db_file = "odio_politica.db"
    
    if not os.path.exists(db_file):
        print("❌ SQLite local não encontrado.")
        return

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 1. Migrar Candidatos
    print("👤 Migrando candidatos...")
    cursor.execute("SELECT username, nome_completo, bio, cargo, sexo, raca, estado, partido, ideologia, seguidores FROM candidatos")
    cols = [c[0] for c in cursor.description]
    rows = cursor.fetchall()
    
    candidatos_data = []
    for r in rows:
        candidatos_data.append(dict(zip(cols, r)))
    
    if candidatos_data:
        upsert_supabase("candidatos", candidatos_data)

    # 2. Migrar Comentários
    print("💬 Migrando comentários...")
    cursor.execute("SELECT id_externo, candidato_id, post_id, autor_username, texto_bruto, data_coleta, data_publicacao, likes FROM comentarios")
    cols = [c[0] for c in cursor.description]
    rows = cursor.fetchall()
    
    comentarios_data = []
    for r in rows:
        item = dict(zip(cols, r))
        # Garante que timestamps nulos ou mal formados não quebrem o Postgres
        if not item.get("data_coleta"): item["data_coleta"] = datetime.now().isoformat()
        comentarios_data.append(item)
    
    if comentarios_data:
        # Divide em lotes de 50 para garantir estabilidade
        for i in range(0, len(comentarios_data), 50):
            batch = comentarios_data[i:i+50]
            upsert_supabase("comentarios", batch)

    conn.close()
    print("🏆 Migração unificada concluída com sucesso!")

def upsert_supabase(table, data):
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    
    try:
        response = httpx.post(url, json=data, headers=headers, timeout=30.0)
        if response.status_code in [200, 201]:
            print(f"   ✅ {len(data)} registros enviados para {table}.")
        else:
            print(f"   ❌ Erro em {table} ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"   ❌ Falha crítica: {e}")

if __name__ == "__main__":
    migrate_to_supabase_v2()
