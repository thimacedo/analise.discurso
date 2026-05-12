
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import httpx
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

def seed_candidatos():
    print("🌱 Populando Candidatos...")
    candidatos = [
        {"username": "alvo_exemplo_1", "nome_completo": "Candidato Alfa", "cargo": "Deputado", "estado": "SP", "status_monitoramento": "Ativo"},
        {"username": "alvo_exemplo_2", "nome_completo": "Candidata Beta", "cargo": "Senadora", "estado": "RJ", "status_monitoramento": "Ativo"},
        {"username": "alvo_exemplo_3", "nome_completo": "Político Gama", "cargo": "Governador", "estado": "DF", "status_monitoramento": "Ativo"},
    ]
    resp = httpx.post(f"{SUPABASE_URL}/rest/v1/candidatos", json=candidatos, headers=HEADERS)
    print(f"✅ Candidatos: {resp.status_code}")

def seed_metrics():
    print("🌱 Populando Métricas Diárias (últimos 15 dias)...")
    metrics = []
    hoje = datetime.now()
    for i in range(15):
        data = (hoje - timedelta(days=i)).strftime('%Y-%m-%d')
        total = random.randint(1000, 5000)
        hate = random.randint(50, 400)
        metrics.append({
            "data": data,
            "total_coletado": total,
            "total_hate": hate,
            "total_neutro": total - hate,
            "resiliencia": round(100 - (hate/total*100), 2),
            "pasa_breakdown": {"AMEACA": random.randint(1, 20), "ODIO_IDENTITARIO": random.randint(1, 30)},
            "uf_breakdown": {"SP": random.randint(1, 50), "RJ": random.randint(1, 40)}
        })
    resp = httpx.post(f"{SUPABASE_URL}/rest/v1/metricas_diarias", json=metrics, headers=HEADERS)
    print(f"✅ Métricas: {resp.status_code}")

def seed_networks():
    print("🌱 Populando Redes Coordenadas...")
    redes = [
        {
            "nome": "Rede Ômega (Teste)", 
            "status": "ATIVA", 
            "descricao": "Rede simulada para teste de interface.",
            "alvos_vinculados": 5,
            "eventos_count": 150,
            "palavras_chave": ["teste", "simulação", "diamond"],
            "severidade": 85
        }
    ]
    resp = httpx.post(f"{SUPABASE_URL}/rest/v1/redes_coordenadas", json=redes, headers=HEADERS)
    print(f"✅ Redes: {resp.status_code}")

if __name__ == "__main__":
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Erro: SUPABASE_URL ou SUPABASE_KEY não configurados no .env")
    else:
        seed_candidatos()
        seed_metrics()
        seed_networks()
        print("\n✨ Seed concluído! Reinicie o dashboard para ver os dados.")
