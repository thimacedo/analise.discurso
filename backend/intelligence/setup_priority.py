import httpx

SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY"
headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json"}

def setup_extra_scrape():
    # 1. Buscar candidatos sem dados ou com dados antigos
    print("🔍 Buscando alvos sem dados de raspagem...")
    r = httpx.get(f"{SB_URL}/candidatos?select=id,username,comentarios_totais_count&or=(comentarios_totais_count.eq.0,comentarios_totais_count.is.null)", headers=headers)
    targets = r.json()
    
    if not targets:
        print("✅ Todos os candidatos possuem dados básicos.")
        return

    print(f"📍 Identificados {len(targets)} alvos para raspagem extra.")
    
    # 2. Marcar como prioridade no Supabase
    for t in targets:
        print(f"Marcando @{t['username']} como PRIORIDADE...")
        httpx.patch(f"{SB_URL}/candidatos?id=eq.{t['id']}", headers=headers, json={"is_priority": True})

    print("\n🚀 Fila de prioridade atualizada no Supabase. O próximo ciclo do worker processará esses alvos primeiro.")

if __name__ == "__main__":
    setup_extra_scrape()
