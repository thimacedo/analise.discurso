import httpx
import asyncio
import time

async def fetch(client, url):
    try:
        resp = await client.get(url)
        return resp.status_code
    except:
        return 0

async def run_test():
    url = "https://sentinela-democratica-ruby.vercel.app/api/health"
    print(f"🚀 Iniciando teste de carga em: {url}")
    start = time.time()
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [fetch(client, url) for _ in range(50)]
        results = await asyncio.gather(*tasks)
    
    end = time.time()
    success = [r for r in results if r != 0]
    print(f"\n--- RELATÓRIO DE CARGA ---")
    print(f"Total de Reqs: {len(results)}")
    print(f"Reqs Completadas: {len(success)}")
    print(f"Tempo Total: {end - start:.2f}s")
    print(f"Reqs/segundo: {len(results)/(end - start):.2f}")
    print(f"Status mais comum: {max(set(results), key=results.count) if results else 'N/A'}")

if __name__ == '__main__':
    asyncio.run(run_test())
