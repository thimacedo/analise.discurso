#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Consolidação de KPIs para o Dashboard do Sentinela
Gera os snapshots em JSON e CSV lidos pelo endpoint /api/v1/summary
"""
import os
import json
import csv
from datetime import datetime
from core.supabase_service import get_supabase_client # Importa a nova função

# Configuração de Paths para o Vercel/Local
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
API_DIR = os.path.join(ROOT_DIR, 'api')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(API_DIR, exist_ok=True)

def update_kpis():
    print("[INFO] Iniciando consolidação de KPIs...")
    client = get_supabase_client() # Usa a nova função para obter o cliente
    if client is None:
        print("[ERRO] Cliente Supabase não inicializado.")
        return
    try:
        # Coleta de Métricas Brutas do Supabase
        # 1. Total de Alvos Ativos
        alvos_res = client.table('candidatos').select('id', count='exact').execute()
        total_alvos = alvos_res.count if alvos_res.count is not None else 0
        
        # 2. Total de Alertas / Falsos Positivos
        alertas_res = client.table('alertas_ativos').select('id', count='exact').execute()
        total_alertas = alertas_res.count if alertas_res.count is not None else 0
        
        # 3. Anúncios Processados
        anuncios_res = client.table('anuncios').select('id', count='exact').execute()
        total_anuncios = anuncios_res.count if anuncios_res.count is not None else 0
        
        # Montagem do Snapshot
        kpi_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {
                "total_alvos": total_alvos,
                "total_alertas": total_alertas,
                "total_anuncios": total_anuncios,
                "resiliencia_score": 98.5
            },
            "status": "active"
        }
        
        # 1. Escrita do JSON Snapshot (Frontend)
        json_path = os.path.join(DATA_DIR, 'kpi_snapshot_latest.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(kpi_data, f, indent=4)
        print(f"[OK] JSON gerado: {json_path}")
        
        # 2. Escrita do CSV Legacy (API retrocompatibilidade)
        csv_path = os.path.join(API_DIR, 'dados_latest.csv')
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['metric', 'value', 'timestamp'])
            writer.writerow(['total_alvos', total_alvos, kpi_data['timestamp']])
            writer.writerow(['total_alertas', total_alertas, kpi_data['timestamp']])
            writer.writerow(['total_anuncios', total_anuncios, kpi_data['timestamp']])
        print(f"[OK] CSV Legacy gerado: {csv_path}")
        
    except Exception as e:
        print(f"[ERRO] Falha na consolidação de KPIs: {str(e)}")
        raise

if __name__ == "__main__":
    update_kpis()
