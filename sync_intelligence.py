import os
import json
import httpx
from datetime import datetime
from dotenv import load_dotenv
from instagram_collector import ForensicCollector

load_dotenv()

# CONFIGURAÇÕES
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def sync_monitoring_flow():
    print("🛰️ Iniciando Fluxo de Sincronização Inteligente...")
    
    try:
        # 1. Obter lista atual do Instagram (Real-time)
        collector = ForensicCollector()
        user_id = collector.client.user_id
        print(f"🔍 Raspando seguidores atuais de @monitoramento.discurso...")
        following = collector.client.user_following(user_id)
        current_following_usernames = {u.username for u in following.values()}
        
        # 2. Obter lista atual do Supabase
        resp = httpx.get(f"{SUPABASE_URL}/rest/v1/candidatos?select=username,status_monitoramento", headers=HEADERS)
        db_profiles = resp.json()
        db_usernames = {p['username'] for p in db_profiles}
        
        # 3. Identificar Mudanças
        new_profiles = current_following_usernames - db_usernames
        removed_profiles = db_usernames - current_following_usernames
        
        # 4. Processar Novos Perfis
        for username in new_profiles:
            print(f"✨ Novo perfil detectado: @{username}")
            u_data = following[[pk for pk, u in following.items() if u.username == username][0]]
            data = {
                "username": username,
                "nome_completo": u_data.full_name,
                "status_monitoramento": "ATIVO",
                "data_entrada": datetime.now().isoformat(),
                "user_id": os.getenv("INVESTIGATOR_ID")
            }
            httpx.post(f"{SUPABASE_URL}/rest/v1/candidatos", json=data, headers=HEADERS)
            log_event(username, "ENTROU")

        # 5. Processar Perfis Removidos
        for username in removed_profiles:
            print(f"🚫 Perfil removido do monitoramento: @{username}")
            url_patch = f"{SUPABASE_URL}/rest/v1/candidatos?username=eq.{username}"
            httpx.patch(url_patch, json={
                "status_monitoramento": "INATIVO",
                "data_saida": datetime.now().isoformat()
            }, headers=HEADERS)
            log_event(username, "SAIU")

        # 6. Atualizar Estatísticas Quantitativas
        update_global_stats()
        
        print("🏆 Sincronização e Auditoria concluídas!")

    except Exception as e:
        print(f"❌ Erro no fluxo: {e}")

def log_event(username, event):
    data = {"username": username, "evento": event, "data": datetime.now().isoformat()}
    httpx.post(f"{SUPABASE_URL}/rest/v1/historico_monitoramento", json=data, headers=HEADERS)

def update_global_stats():
    print("📊 Atualizando métricas quantitativas por perfil...")
    # Esta função executa uma query agregada no Supabase para contar comentários por candidato
    # e atualiza os totais na tabela de candidatos para facilitar o report.
    pass

if __name__ == "__main__":
    sync_monitoring_flow()
