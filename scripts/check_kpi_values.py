import sys
import os

# Força UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.append(r"C:\projetos\sentinela-democratica")
from core.db import db_client

def get_latest():
    print("=== MÉTRICAS DIÁRIAS (ÚLTIMO REGISTRO) ===")
    try:
        res_metrics = db_client.client.table('metricas_diarias').select('*').order('data', desc=True).limit(1).execute()
        if res_metrics.data:
            for k, v in res_metrics.data[0].items():
                print(f"{k}: {v}")
        else:
            print("Nenhuma métrica encontrada.")
    except Exception as e:
        print(f"Erro ao buscar métricas: {e}")

    print("\n=== ÚLTIMA REDE COORDENADA DETECTADA ===")
    try:
        res_redes = db_client.client.table('redes_coordenadas').select('*').order('created_at', desc=True).limit(1).execute()
        if res_redes.data:
            for k, v in res_redes.data[0].items():
                print(f"{k}: {v}")
        else:
            print("Nenhuma rede coordenada encontrada.")
    except Exception as e:
        print(f"Erro ao buscar redes: {e}")

if __name__ == '__main__':
    get_latest()
