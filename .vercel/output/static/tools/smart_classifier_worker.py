
import asyncio
import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path para encontrar o pacote core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ai_service import ai_service
from core.supabase_service import get_supabase_client

async def smart_worker():
    backoff = 0
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🛡️ SMART CLASSIFIER WORKER ATIVADO.")
    
    while True:
        if backoff > 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏳ Aguardando {backoff}s (respeitando rate limit)...")
            await asyncio.sleep(backoff)
            backoff = 0
        
        try:
            # Busca uma pequena amostra para verificar se há trabalho
            comments = await db_client.fetch_unprocessed_comments(limit=10)
            if not comments:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 💤 Nada pendente. Pausa de 60s.")
                await asyncio.sleep(60)
                continue
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 Processando lote de {len(comments)} comentários...")
            # O run_batch_classification já lida com a cascata de motores
            processed = await ai_service.run_batch_classification(limit=10)
            
            if processed == 0:
                # Se não processou nada, provavelmente todas as APIs deram 429 ou falharam
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 Falha total no lote. Iniciando backoff de 90s.")
                backoff = 90
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ {processed} comentários processados com sucesso.")
                # Pausa curta entre lotes de sucesso para não sobrecarregar
                await asyncio.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 Worker interrompido manualmente.")
            break
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Erro inesperado: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    try:
        asyncio.run(smart_worker())
    except KeyboardInterrupt:
        pass
