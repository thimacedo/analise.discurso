import json
import httpx

def sync_master_profiles():
    print("🛰️ Sincronizando perfis mestres com Supabase...")
    
    with open('perfis_monitorados.json', 'r', encoding='utf-8') as f:
        profiles = json.load(f)

    # Prepara dados (135 perfis)
    candidatos = [{'username': p['username'], 'nome_completo': p.get('full_name', '')} for p in profiles]

    headers = {
        'apikey': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY",
        'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY",
        'Content-Type': 'application/json',
        'Prefer': 'resolution=merge-duplicates'
    }

    url = 'https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1/candidatos'
    
    try:
        # Envia em blocos para segurança
        for i in range(0, len(candidatos), 50):
            batch = candidatos[i:i+50]
            response = httpx.post(url, json=batch, headers=headers)
            if response.status_code in [200, 201]:
                print(f"   ✅ Bloco {i//50 + 1} sincronizado.")
            else:
                print(f"   ❌ Erro no bloco: {response.text}")
        
        print(f"🏆 Total de {len(candidatos)} perfis prontos no Cloud.")
        
    except Exception as e:
        print(f"❌ Falha: {e}")

if __name__ == "__main__":
    sync_master_profiles()
