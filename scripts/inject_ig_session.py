"""
PASA v49.6 - Multi-Session Injector
Injeta múltiplas sessões do Instagram no banco de dados para suporte a fallback.
"""
from core.supabase_service import supabase
from datetime import datetime, timezone

def inject_sessions():
    sessions = [
        "53127160841:jLDQgp8A4tIrUW:4:AYiQC8sfn_eIM4dppMAY7APcdpyPqBtsjnspZF2AqQ",
        "29815807006:qp2klXORQPHnTJ:3:AYgwuJQA4cvHjcMQEYKiLCrrZn5R008iIjDpouXIyA"
    ]
    
    print(f"[SessionInjector] Iniciando injeção de {len(sessions)} sessões...")
    
    for session_id in sessions:
        print(f" -> Processando: {session_id[:20]}...")
        data = {
            "plataforma": "instagram",
            "cookies": f"sessionid={session_id}",
            "status": "active",
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # PASA v49.6: Usa a restrição composta (plataforma, cookies)
            res = supabase.table('worker_sessions').upsert(data, on_conflict='plataforma,cookies').execute()
            print(f"    ✅ Sucesso.")
        except Exception as e:
            print(f"    ❌ Erro: {e}")

if __name__ == "__main__":
    inject_sessions()
