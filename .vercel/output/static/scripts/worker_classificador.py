import asyncio
import sys
import os
from datetime import datetime

# Força UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Ajusta path
sys.path.append(r".")
from core.ai_service import ai_service
from core.config import settings

async def run_with_timeout(coro, timeout):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        print(f"⏰ [TIMEOUT] Lote de IA demorou demais. Abortando tentativa...")
        return 0

async def classification_worker():
    print(f"--- [WORKER SOLENYA] Iniciado (Provider: {settings.IA_PROVIDER}) ---")
    
    while True:
        try:
            now = datetime.now().strftime('%H:%M:%S')
            print(f"[{now}] 🔍 Buscando lote...")
            
            # Tenta processar o lote com um timeout de 5 minutos (300s)
            # Se o Ollama travar, o asyncio corta ele.
            processed_count = await run_with_timeout(ai_service.run_batch_classification(limit=50), 300)
            
            if processed_count > 0:
                print(f"OK [{now}] Processados {processed_count} comentários.")
            else:
                print(f"ZZZ [{now}] Nada pendente ou falha. Descansando 30s...")
                await asyncio.sleep(30)
            
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"ERROR [{datetime.now().strftime('%H:%M:%S')}] {e}")
            await asyncio.sleep(10)

if __name__ == '__main__':
    try:
        asyncio.run(classification_worker())
    except KeyboardInterrupt:
        print("\nWorker interrompido.")
