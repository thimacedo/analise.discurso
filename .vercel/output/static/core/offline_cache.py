"""
PASA v35 - Offline Cache: Fila de resiliência local.
Se o Supabase cair, os dados são salvos aqui até a conexão voltar.
"""
import os
import json
from datetime import datetime

CACHE_DIR = "data/cache"
QUEUE_FILE = os.path.join(CACHE_DIR, "offline_queue.json")

def _ensure_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def save_to_queue(data_type: str, payload: dict):
    """Salva dados no cache local se o Supabase estiver offline."""
    _ensure_dir()
    queue = load_queue()
    queue.append({
        "type": data_type,
        "payload": payload,
        "timestamp": datetime.now().isoformat()
    })
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)

def load_queue() -> list:
    """Carrega a fila de cache local."""
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def flush_queue(db_client) -> int:
    """Tenta esvaziar a fila local enviando tudo para o Supabase."""
    queue = load_queue()
    if not queue:
        return 0

    success_count = 0
    for item in queue:
        try:
            table_name = item['type']
            db_client.table(table_name).insert(item['payload']).execute()
            success_count += 1
        except Exception as e:
            print(f"[OfflineCache] Falha ao sincronizar item: {e}")
            break # Para no primeiro erro para não pular ordem

    # Remove itens sincronizados com sucesso
    if success_count > 0:
        remaining = queue[success_count:]
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(remaining, f, ensure_ascii=False, indent=2)

    return success_count
