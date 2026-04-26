import os
import json
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# CONFIGURAÇÕES
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SENTINELA_SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def sync_monitoring_flow():
    """
    Novo Fluxo de Sincronização (v15.5.0)
    Desacoplado do Instagram Following. A fonte da verdade agora é o Banco de Dados.
    """
    print("🛰️ Iniciando Fluxo de Sincronização de Alvos (Resiliente)...")
    
    try:
        # 1. Obter lista atual de alvos ATIVOS do Supabase
        resp = httpx.get(f"{SUPABASE_URL}/rest/v1/candidatos?select=username,nome_completo,status_monitoramento&status_monitoramento=eq.Ativo", headers=HEADERS)
        if resp.status_code != 200:
            print(f"❌ Erro ao consultar banco: {resp.status_code} - {resp.text}")
            return
            
        active_targets = resp.json()
        print(f"📊 Alvos monitorados no banco: {len(active_targets)}")

        # 2. Atualizar Cache Local para os Workers (Otimização)
        os.makedirs("data", exist_ok=True)
        with open("data/active_targets_cache.json", "w", encoding="utf-8") as f:
            json.dump(active_targets, f, indent=4, ensure_ascii=False)
        
        # 3. Atualizar Estatísticas Quantitativas
        update_global_stats()
        
        print("🏆 Sincronização de alvos e auditoria concluídas!")

    except Exception as e:
        print(f"❌ Erro no fluxo: {e}")

def log_event(username, event):
    data = {"username": username, "evento": event, "data": datetime.now().isoformat()}
    httpx.post(f"{SUPABASE_URL}/rest/v1/historico_monitoramento", json=data, headers=HEADERS)

def update_global_stats():
    print("📊 Atualizando métricas quantitativas por perfil...")
    # Lógica de agregação mantida conforme necessidade futura
    pass

if __name__ == "__main__":
    sync_monitoring_flow()
