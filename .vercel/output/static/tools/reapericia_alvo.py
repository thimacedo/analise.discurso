import asyncio
import os
from core.db import db_client
from core.ai_service import run_batch_classification

async def reevaluate_target(username: str):
    """
    Executa re-perícia manual para um alvo.
    """
    print(f"🕵️‍♂️ [Sentinela] Iniciando RE-PERÍCIA manual: @{username}")
    
    await db_client.reset_target_comments(username)
    await db_client.mark_repericia_complete(username)
    
    print(f"✅ Reset concluído. Disparando motor de Inteligência Diamond...")
    await run_batch_classification(limit=500)
    
    print(f"\n✨ RE-PERÍCIA FINALIZADA para @{username}!")

if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else "cabodaciolo"
    asyncio.run(reevaluate_target(target))
