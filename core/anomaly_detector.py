import os
import requests
import json
from datetime import datetime, timedelta

# Configurações do Supabase
SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "SUPABASE_KEY_PLACEHOLDER")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json" }

def detect_anomalies():
    print("🧠 SENTINELA CORE: Iniciando Motor de Detecção de Anomalias (Fase 3)...")
    
    # 1. Recuperar últimos dados de monitorados
    res = requests.get(f"{SUPABASE_URL}/rest/v1/candidatos?select=username,comentarios_totais_count,comentarios_odio_count", headers=HEADERS)
    if res.status_code != 200: return
    
    data = res.json()
    anomalies = []

    for c in data:
        hate_ratio = (c['comentarios_odio_count'] / c['comentarios_totais_count']) if (c.get('comentarios_totais_count') or 0) > 0 else 0
        
        # Lógica Preditiva Otimizada para o Lote v15.2 (Sensibilidade Alta para Teste)
        if hate_ratio > 0.05 or (c.get('comentarios_totais_count', 0) > 1000):
            anomalies.append({
                "username": c['username'],
                "momentum": round(hate_ratio * 100, 2),
                "status": "ALERTA DE ONDA" if hate_ratio > 0.10 else "ESTÁVEL",
                "timestamp": datetime.now().isoformat()
            })

    # Sort por momentum e limitar
    anomalies = sorted(anomalies, key=lambda x: x['momentum'], reverse=True)[:5]

    # 3. Gerar arquivo de cache para o Frontend (Latência Zero)
    os.makedirs("data", exist_ok=True)
    with open("data/predictive_trends.json", "w", encoding="utf-8") as f:
        json.dump(anomalies, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Motor Preditivo Sincronizado. {len(anomalies)} anomalias detectadas.")

if __name__ == "__main__":
    detect_anomalies()
