import sys
import os
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Configuração de caminhos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'core')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'collectors')))

from instagram_collector import ForensicCollector
from local_qwen_classifier import QwenLocalClassifier
from database.repository import DatabaseRepository

load_dotenv()

VERCEL_API_URL = os.getenv("VERCEL_API_URL", "https://projeto-odio-politica.vercel.app/api/v1")
DASHBOARD_PIN = os.getenv("DASHBOARD_PIN", "1234")

# ESCALONAMENTO NACIONAL SOLICITADO
CANDIDATES = [
    "lulaoficial", 
    "flaviobolsonaro",
    "jairmessiasbolsonaro",
    "nikolasferreiradm",
    "gleisihoffmann",
    "choquei",
    "metropoles"
]

def emoji_safe_print(text):
    try: print(text)
    except: print(text.encode('ascii', 'ignore').decode('ascii'))

def push_to_cloud(data_list: list):
    try:
        headers = {'X-PIN': DASHBOARD_PIN, 'Content-Type': 'application/json'}
        res = requests.post(f"{VERCEL_API_URL}/sync", headers=headers, json=data_list, timeout=20)
        if res.status_code == 200:
            emoji_safe_print(f"✅ Sincronizados {len(data_list)} itens com a nuvem.")
        else:
            emoji_safe_print(f"❌ Falha cloud: {res.status_code}")
    except Exception as e:
        emoji_safe_print(f"⚠️ Erro conexão nuvem: {e}")

def run_mass_analysis():
    emoji_safe_print("="*60)
    emoji_safe_print("FORENSENET v5.2 - MASSIVE CONTEXTUAL COLLECTION")
    emoji_safe_print("="*60)
    
    db = DatabaseRepository()
    db.criar_tabelas()
    classifier = QwenLocalClassifier()
    collector = ForensicCollector()
    
    for username in CANDIDATES:
        emoji_safe_print(f"\n🚀 Alvo: @{username}")
        try:
            # Aumentando volume: 20 posts por candidato, 30 comentários por post
            raw_df = collector.monitor_multiple_candidates([username], posts_per_candidate=20)
            
            if raw_df.empty:
                emoji_safe_print(f"ℹ️ Sem dados novos para @{username}.")
                continue
            
            sync_payload = []
            for _, row in raw_df.iterrows():
                # 1. Salvar Local (Custódia)
                candidato = db.salvar_candidato(row['candidate'], {})
                comentario = db.salvar_comentario(candidato.id, {
                    'id_externo': str(row['id']),
                    'post_id': str(row['post_id']), # Contexto preservado
                    'autor_username': row['owner_username'],
                    'texto_bruto': row['text'],
                    'data_publicacao': pd.to_datetime(row['timestamp'])
                })
                
                # 2. IA Pericial Local
                res = classifier.classify_comment(row['text'])
                
                db.salvar_classificacao(comentario.id, {
                    'categoria_odio': res.get('category', 'NEUTRO'),
                    'score': float(res.get('score', 0.0)),
                    'confianca': float(res.get('confidence', 0.0)),
                    'modelo_versao': 'qwen-v5.2-local'
                })
                
                # 3. Payload para Cloud (v5.2 format)
                sync_payload.append({
                    "id_external": str(row['id']),
                    "candidato": username,
                    "autor": row['owner_username'],
                    "texto": row['text'],
                    "data": row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                    "categoria": res.get('category', 'NEUTRO'),
                    "score": float(res.get('score', 0.0)),
                    "post_url": str(row['post_id']),
                    "post_image": row.get('post_image'), # Novo campo
                    "post_caption": row.get('post_caption') # Novo campo
                })
            
            if sync_payload:
                push_to_cloud(sync_payload)
            
        except Exception as e:
            emoji_safe_print(f"❌ Erro em @{username}: {e}")
            continue

    emoji_safe_print("\n" + "="*60)
    emoji_safe_print("RODADA MASSIVA FINALIZADA")
    emoji_safe_print("="*60)

if __name__ == "__main__":
    run_mass_analysis()
