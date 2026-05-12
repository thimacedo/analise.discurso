
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import sys
import asyncio
import time
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para importar core
sys.path.append(os.getcwd())

from core.ai_service import run_batch_classification
from core.supabase_service import get_supabase_client

async def main():
    print("🚀 IA TURBO: Processando fila de comentários (Sem Scraper)...")
    
    while True:
        # Busca pendentes via REST direto para contagem rápida
        comentarios = await db_client.fetch_unprocessed_comments(limit=1)
        if not comentarios:
            print("✨ Fila de IA zerada com sucesso!")
            break
            
        print("⚡ Iniciando processamento de lote...")
        try:
            await run_batch_classification(limit=200)
        except Exception as e:
            print(f"⚠️ Erro no ciclo de IA: {e}")
            break
        
        # Pausa curta para evitar sobrecarga
        await asyncio.sleep(1)

    print("\n✅ OPERAÇÃO IA CONCLUÍDA.")

if __name__ == "__main__":
    asyncio.run(main())
