import httpx
import asyncio

async def test_remote_api():
    base_url = "https://sentinela-democratica.vercel.app" # URL principal curta
    preview_url = "https://sentinela-democratica-ctwfosv7u-thimacedos-projects.vercel.app"
    
    endpoints = [
        "/api/v1/summary",
        "/api/v1/trends",
        "/api/v1/pasa/breakdown",
        "/api/v1/geo/uf",
        "/api/health"
    ]
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        print(f"🌐 Testando Produção: {base_url}")
        for ep in endpoints:
            try:
                r = await client.get(f"{base_url}{ep}")
                print(f"  {ep} -> {r.status_code}")
            except Exception as e:
                print(f"  {ep} -> ERRO: {e}")

        print(f"\n🌐 Testando Preview (Logs): {preview_url}")
        for ep in endpoints:
            try:
                r = await client.get(f"{preview_url}{ep}")
                print(f"  {ep} -> {r.status_code}")
            except Exception as e:
                print(f"  {ep} -> ERRO: {e}")

if __name__ == "__main__":
    asyncio.run(test_remote_api())
