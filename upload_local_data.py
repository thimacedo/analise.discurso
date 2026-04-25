import json
import httpx
import os

SB_URL = "https://vhamejkldzxbeibqeqpk.supabase.co/rest/v1"
SB_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY"
headers = {"apikey": SB_KEY, "Authorization": f"Bearer {SB_KEY}", "Content-Type": "application/json"}

def sync():
    data_path = r"E:\projetos\sentinela-democratica\data\classified_profiles.json"
    if not os.path.exists(data_path):
        print("❌ Arquivo local não encontrado.")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    print(f"🚀 Sincronizando {len(profiles)} perfis locais...")
    
    count = 0
    for p in profiles:
        username = p.get("username")
        comments = p.get("comments") or 0
        
        # Só subir se tiver dados reais (comentários > 0)
        if comments > 0:
            print(f"Subindo @{username}: {comments} comentários.")
            # Buscar ID no Supabase
            r_get = httpx.get(f"{SB_URL}/candidatos?username=eq.{username}&select=id", headers=headers)
            res_get = r_get.json()
            
            if res_get:
                cid = res_get[0]['id']
                # Como não temos o count de ódio processado no JSON local de forma explícita,
                # vamos subir o total e marcar a data para o PASA Worker reavaliar se necessário,
                # ou assumir uma proporção base para impacto visual se o usuário desejar.
                # Por ora, subimos apenas o total real coletado.
                httpx.patch(f"{SB_URL}/candidatos?id=eq.{cid}", headers=headers, json={
                    "comentarios_totais_count": comments,
                    "data_ultima_analise": "2026-04-24T00:00:00Z" # Retroativo à data do arquivo
                })
                count += 1

    print(f"\n✅ Sincronização concluída! {count} perfis atualizados no Supabase.")

if __name__ == "__main__":
    sync()
