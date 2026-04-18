import sys
import os
import requests
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Configuração de caminhos para os novos diretórios
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'core')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'collectors')))

from instagram_collector import ForensicCollector
from local_qwen_classifier import QwenLocalClassifier
from database.repository import DatabaseRepository

load_dotenv()

# Configurações de Nuvem para Sincronização Gradual
VERCEL_API_URL = os.getenv("VERCEL_API_URL", "https://analise-discurso.vercel.app/api/v1")
DASHBOARD_PIN = os.getenv("DASHBOARD_PIN", "1234")

def emoji_safe_print(text):
    """Imprime no console removendo emojis apenas para evitar erro de encoding no Windows."""
    try:
        print(text)
    except UnicodeEncodeError:
        clean_text = text.encode('ascii', 'ignore').decode('ascii')
        print(clean_text)

def get_monitored_candidates():
    try:
        # Perfis agora estão na pasta data/
        perfis_path = os.path.join('data', 'perfis_monitorados.json')
        if not os.path.exists(perfis_path):
            perfis_path = 'perfis_monitorados.json' # fallback

        with open(perfis_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [p['username'] for p in data.get('perfis_detalhes', [])]
    except Exception as e:
        emoji_safe_print(f"Erro ao ler perfis_monitorados.json: {e}")
        return ["jairmessiasbolsonaro", "lulaoficial"]

CANDIDATES = get_monitored_candidates()

def push_to_cloud(data_list: list):
    """Envia um lote de dados para o sistema online gradualmente."""
    try:
        headers = {'X-PIN': DASHBOARD_PIN, 'Content-Type': 'application/json'}
        res = requests.post(f"{VERCEL_API_URL}/sync", headers=headers, json=data_list, timeout=10)
        if res.status_code == 200:
            emoji_safe_print(f"Sincronizados {len(data_list)} itens com a nuvem.")
        else:
            emoji_safe_print(f"Falha na sincronização cloud: {res.status_code}")
    except Exception as e:
        emoji_safe_print(f"Erro de conexão com a nuvem: {e}")

def run_full_analysis():
    emoji_safe_print("="*60)
    emoji_safe_print("FORENSENET v2.3 - MONITORAMENTO REAL-TIME & EMOJI-SAFE")
    emoji_safe_print("="*60)
    
    db = DatabaseRepository()
    db.criar_tabelas()
    classifier = QwenLocalClassifier()
    collector = ForensicCollector()
    
    for username in CANDIDATES:
        emoji_safe_print(f"\n--- Iniciando Coleta de @{username} ---")
        try:
            # 1. Coleta do Candidato Atual
            raw_df = collector.monitor_multiple_candidates([username], posts_per_candidate=10)
            
            if raw_df.empty:
                emoji_safe_print(f"Sem dados para @{username}.")
                continue
            
            emoji_safe_print(f"Coletados {len(raw_df)} comentarios de @{username}.")
            
            # 2. Classificação Local
            classificacoes = []
            sync_payload = []
            
            for _, row in raw_df.iterrows():
                # Salva localmente primeiro
                candidato = db.salvar_candidato(row['candidate'], {})
                comentario = db.salvar_comentario(candidato.id, {
                    'id_externo': str(row['id']),
                    'post_id': str(row['post_id']),
                    'autor_username': row['owner_username'],
                    'texto_bruto': row['text'],
                    'data_publicacao': pd.to_datetime(row['timestamp'])
                })
                
                # Classifica
                res = classifier.classify_comment(row['text'])
                
                db.salvar_classificacao(comentario.id, {
                    'categoria_odio': res.get('category', 'NEUTRO'),
                    'score': float(res.get('score', 0.0)),
                    'confianca': float(res.get('confidence', 0.0)),
                    'modelo_versao': 'qwen2.5-coder-local'
                })
                
                # Prepara para a Nuvem
                sync_payload.append({
                    "id_external": str(row['id']),
                    "candidato": username,
                    "autor": row['owner_username'],
                    "texto": row['text'],
                    "data": row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp']),
                    "categoria": res.get('category', 'NEUTRO'),
                    "score": float(res.get('score', 0.0)),
                    "confianca": float(res.get('confidence', 0.0))
                })
            
            # 3. PUSH PARA A NUVEM
            emoji_safe_print(f"Enviando dados de @{username} para o Dashboard Online...")
            push_to_cloud(sync_payload)
            
        except Exception as e:
            emoji_safe_print(f"Erro no processamento de @{username}: {e}")
            continue

    emoji_safe_print("\n" + "="*60)
    emoji_safe_print("RODADA DE MONITORAMENTO FINALIZADA")
    emoji_safe_print("="*60)

if __name__ == "__main__":
    run_full_analysis()
