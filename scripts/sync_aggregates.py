import os
import requests

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json" }

def sync_aggregates():
    print("🔄 Sincronizando agregados de comentários (baseado em username)...")
    
    # 1. Pegar todos os candidatos
    res = requests.get(f"{SUPABASE_URL}/rest/v1/candidatos?select=id,username", headers=HEADERS)
    candidatos = res.json()
    
    for c in candidatos:
        cand_id = c['id']
        username = c['username']
        
        # 2. Contar comentários totais usando o username como ID de referência na tabela comentarios
        res_total = requests.get(
            f"{SUPABASE_URL}/rest/v1/comentarios?candidato_id=eq.{username}&select=id", 
            headers={**HEADERS, "Prefer": "count=exact"}
        )
        total = int(res_total.headers.get("Content-Range", "0/0-0").split("/")[-1])
        
        # 3. Contar comentários de ódio
        res_odio = requests.get(
            f"{SUPABASE_URL}/rest/v1/comentarios?candidato_id=eq.{username}&is_hate=eq.true&select=id", 
            headers={**HEADERS, "Prefer": "count=exact"}
        )
        odio = int(res_odio.headers.get("Content-Range", "0/0-0").split("/")[-1])
        
        if total > 0:
            print(f"  📈 @{username}: {total} total, {odio} ódio. Atualizando...")
            update_data = {
                "comentarios_totais_count": total,
                "comentarios_odio_count": odio
            }
            requests.patch(f"{SUPABASE_URL}/rest/v1/candidatos?id=eq.{cand_id}", headers=HEADERS, json=update_data)

if __name__ == "__main__":
    sync_aggregates()
