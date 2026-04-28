import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.getenv("SENTINELA_SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

PROFILES = [
    "kimkataguiri", "tcuoficial", "jeronimorodriguesba", 
    "helderbarbalho", "eduardobolsonaro", "alvarodiasrn", "styvensonvalentim"
]

def restore():
    print("🚑 Iniciando Restauração de Emergência do Monitoramento...")
    for username in PROFILES:
        url = f"{SUPABASE_URL}/rest/v1/candidatos?username=eq.{username}"
        data = {
            "status_monitoramento": "ATIVO",
            "data_saida": None
        }
        try:
            resp = httpx.patch(url, json=data, headers=HEADERS)
            if resp.status_code in [200, 204]:
                print(f"✅ @{username} restaurado para status ATIVO.")
            else:
                print(f"⚠️ Erro ao restaurar @{username}: {resp.status_code}")
        except Exception as e:
            print(f"❌ Falha crítica em @{username}: {e}")

if __name__ == "__main__":
    restore()
