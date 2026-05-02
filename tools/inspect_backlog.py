import os
import httpx
from dotenv import load_dotenv

load_dotenv()

def inspect_unclassified():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    print("🔍 [INSPECT] Buscando comentários pendentes de classificação...")
    
    try:
        # Busca total de pendentes
        r_count = httpx.get(f"{url}/rest/v1/comentarios?processado_ia=eq.false&select=id", headers=headers)
        total = len(r_count.json()) if r_count.status_code == 200 else "???"
        
        # Busca amostra
        r = httpx.get(
            f"{url}/rest/v1/comentarios?processado_ia=eq.false&select=autor_username,texto_bruto,data_coleta,candidato_id&limit=15&order=data_coleta.desc", 
            headers=headers
        )
        
        if r.status_code == 200:
            data = r.json()
            print(f"\n📊 Total Pendente: {total}")
            print("-" * 60)
            for i, c in enumerate(data, 1):
                user = c.get('autor_username', 'anon')
                target = c.get('candidato_id', '???')
                text = c.get('texto_bruto', '').replace('\n', ' ')[:120]
                date = c.get('data_coleta', '')[:19]
                print(f"{i:02d}. [{date}] @{user} (Alvo: @{target})")
                print(f"    💬 \"{text}...\"\n")
        else:
            print(f"❌ Erro Supabase: {r.status_code} - {r.text}")
            
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")

if __name__ == "__main__":
    inspect_unclassified()
