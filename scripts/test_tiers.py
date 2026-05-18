import asyncio
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.workers.instagram_worker import InstagramWorker

async def test_tier_system():
    """Testa o sistema de fallback de tiers."""
    
    worker = InstagramWorker()
    
    # Substitua pelos valores reais para um teste manual se necessário
    target = "lulaoficial"  
    
    print("🧪 Testando sistema de Tiers...")
    print(f"Target: @{target}\n")
    
    # O Worker busca cookies automaticamente do Supabase
    success = worker.run(target)
    
    if success:
        print(f"\n✅ Execução concluída com sucesso para @{target}")
    else:
        print(f"\n❌ Falha na coleta para @{target}")

if __name__ == '__main__':
    asyncio.run(test_tier_system())
