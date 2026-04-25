import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def enrich_candidatos():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    
    # Mapeamento manual para os monitorados conhecidos
    mapping = {
        "lulaoficial": {"estado": "DF", "scope": "NACIONAL"},
        "jairmessiasbolsonaro": {"estado": "DF", "scope": "NACIONAL"},
        "deputadotaveirajr": {"estado": "RN", "scope": "REGIONAL"},
        "verpretoaquino": {"estado": "RN", "scope": "REGIONAL"},
        "fatimabezerrapetista": {"estado": "RN", "scope": "REGIONAL"},
        "rogeriomarinho": {"estado": "RN", "scope": "NACIONAL"},
        "styvensonvalentim": {"estado": "RN", "scope": "NACIONAL"},
        "allysonbezerra.rn": {"estado": "RN", "scope": "REGIONAL"},
        "erikahiltonoficial": {"estado": "SP", "scope": "NACIONAL"},
        "nikolasferreirainfo": {"estado": "MG", "scope": "NACIONAL"},
        "joaocampos": {"estado": "PE", "scope": "REGIONAL"},
        "tarcisiogdf": {"estado": "SP", "scope": "REGIONAL"}
    }
    
    async with httpx.AsyncClient() as client:
        for username, data in mapping.items():
            print(f"📍 Enriquecendo @{username} -> {data['estado']}")
            await client.patch(
                f"{url}/rest/v1/candidatos?username=eq.{username}",
                json={"estado": data['estado']},
                headers=headers
            )
        
        # Marcador genérico para os outros
        await client.patch(
            f"{url}/rest/v1/candidatos?estado=is.null",
            json={"estado": "DF"},
            headers=headers
        )

if __name__ == "__main__":
    asyncio.run(enrich_candidatos())
