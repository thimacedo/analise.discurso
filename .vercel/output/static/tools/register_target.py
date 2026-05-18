
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import sys
from pathlib import Path
from datetime import datetime, UTC

# Garante o path do projeto
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.supabase_service import get_supabase_client

async def register_influencer():
    username = "julianagarcia.br"
    nome = "Juliana Garcia"
    prioridade = 5 # Prioridade Máxima
    
    print(f"💎 Cadastrando @{username} com prioridade {prioridade}...")
    
    try:
        # Upsert na tabela de candidatos
        db_client.client.table('candidatos').upsert({
            "username": username,
            "nome_completo": nome,
            "cargo": "Influenciador",
            "prioridade_coleta": prioridade,
            "status_monitoramento": "Ativo",
            "nota_relevancia": 50.0, # (CargoWeight 5 * 10)
            "atualizado_em": datetime.now(UTC).isoformat()
        }, on_conflict="username").execute()
        
        # Inserir na fila de coleta de hoje para raspagem imediata
        today = datetime.now(UTC).date().isoformat()
        db_client.client.table('fila_coleta').upsert({
            "candidato_id": username,
            "prioridade": prioridade,
            "status": "PENDENTE",
            "data_agendada": today,
            "updated_at": datetime.now(UTC).isoformat()
        }, on_conflict="candidato_id,data_agendada").execute()
        
        print(f"✨ @{username} cadastrada e agendada para hoje!")
    except Exception as e:
        print(f"❌ Erro ao cadastrar: {e}")

if __name__ == "__main__":
    asyncio.run(register_influencer())
