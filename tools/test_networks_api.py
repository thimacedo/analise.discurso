import httpx
import asyncio
import sys
import os

async def test_networks():
    print("🧪 Testando endpoint /api/v1/networks...")
    async with httpx.AsyncClient() as client:
        # Tenta conectar ao localhost (ajuste a porta se necessário)
        try:
            r = await client.get("http://localhost:8000/api/v1/networks")
            print(f"Status: {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                print(f"Sucesso! Encontrados {len(data.get('nodes', []))} nós.")
                return True
            else:
                print(f"Falha esperada: {r.status_code}")
                return False
        except Exception as e:
            print(f"Erro de conexão (servidor offline): {e}")
            return False

if __name__ == "__main__":
    asyncio.run(test_networks())
