import asyncio
import argparse
import time
import sys
import json
from core.supabase_service import get_next_targets_to_scrape, update_last_scraped_at, save_scrape_error
from workers.scrapers.instagram_worker import InstagramWorker

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

async def run_long_scrape(limit=5):
    print(f"🔄 Iniciando Long Scrape Orchestrator (Limite: {limit} alvos)")
    targets = get_next_targets_to_scrape(limit=limit)
    
    if not targets:
        print("✅ Nenhum alvo pendente na fila.")
        return

    print(f"📋 Encontrados {len(targets)} alvos na fila para esta rodada.")
    
    for target in targets:
        username = target.get('username')
        print(f"\n" + "="*50)
        print(f"🎯 PROCESSANDO ALVO: @{username}")
        print("="*50)
        
        start_time = time.time()
        worker = InstagramWorker(username, max_posts=3)
        
        try:
            # Executa o worker
            dados = await worker.execute()
            elapsed = time.time() - start_time
            
            # Cálculo de Métricas
            total_extracted = len(dados) if dados else 0
            hate_count = sum(1 for d in (dados or []) if d.get('is_hate'))
            
            categorias = {}
            if dados:
                for d in dados:
                    cat = d.get('categoria_ia', 'UNKNOWN')
                    categorias[cat] = categorias.get(cat, 0) + 1
                    
            print(f"✅ SUCESSO: @{username}")
            print(f"⏱️ Tempo: {elapsed:.2f}s")
            print(f"📊 Total Extraído: {total_extracted} itens")
            print(f"🚨 Críticos (Hate): {hate_count}")
            print(f"🏷️ Distribuição PASA: {json.dumps(categorias, ensure_ascii=False)}")
            
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ FALHA FATAL: @{username}")
            print(f"⏱️ Tempo até falha: {elapsed:.2f}s")
            print(f"⚠️ Erro: {str(e)}")
            save_scrape_error(username, str(e))
            
        finally:
            print(f"❄️ Atualizando timestamp de fila para @{username} (last_scraped_at)...")
            update_last_scraped_at(username)
            
        # Pausa humana entre perfis para evitar shadowban na sessão
        print("⏳ Aguardando 10 segundos antes do próximo alvo (Cool-down)...")
        await asyncio.sleep(10)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=2, help="Número de alvos para processar nesta rodada")
    args = parser.parse_args()
    asyncio.run(run_long_scrape(limit=args.limit))