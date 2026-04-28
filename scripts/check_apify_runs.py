import os
import requests
import json

APIFY_TOKEN = os.environ.get("SENTINELA_APIFY_API_TOKEN")
RUNS = ["CITigSSwhJws56qyE", "s8eGaihDicPlKBSND", "NQuxtCc4sLvUWQ1vp", "JrgQTlbi1J367UOcP"]

def check_runs():
    print("📋 Status da Raspagem Massiva (DE TODOS os Lotes):")
    for run_id in RUNS:
        try:
            res = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_TOKEN}")
            if res.status_code == 200:
                data = res.json()['data']
                print(f"  - Run {run_id}: {data['status']} | Início: {data['startedAt']}")
            else:
                print(f"  - Run {run_id}: Erro {res.status_code}")
        except Exception as e:
            print(f"  - Run {run_id}: Falha {e}")

if __name__ == "__main__":
    check_runs()
