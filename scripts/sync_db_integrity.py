import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

async def sync_integrity():
    """
    Sincroniza os contadores agregados da tabela 'candidatos' 
    com base nos registros reais da tabela 'comentarios'.
    """
    print("🔄 Iniciando Verificação de Integridade Pericial...")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1. Obter contagens reais do banco via agregação (se possível) ou contagem manual
        # Para performance, buscamos todos os candidatos
        res_can = await client.get(f"{SUPABASE_URL}/rest/v1/candidatos?select=username", headers=headers)
        if res_can.status_code != 200: return
        candidatos = res_can.json()

        for c in candidatos:
            un = c['username']
            
            # Contagem de Totais
            res_total = await client.get(f"{SUPABASE_URL}/rest/v1/comentarios?candidato_id=eq.{un}&select=id", headers=headers)
            total = len(res_total.json()) if res_total.status_code == 200 else 0
            
            # Contagem de Ódio (is_hate=true)
            res_odio = await client.get(f"{SUPABASE_URL}/rest/v1/comentarios?candidato_id=eq.{un}&is_hate=eq.true&select=id", headers=headers)
            odio = len(res_odio.json()) if res_odio.status_code == 200 else 0
            
            # Atualizar Candidato se houver divergência
            update_data = {
                "comentarios_totais_count": total,
                "comentarios_odio_count": odio,
                "atualizado_em": "now()"
            }
            
            await client.patch(f"{SUPABASE_URL}/rest/v1/candidatos?username=eq.{un}", headers=headers, json=update_data)
            print(f"✅ @{un}: {total} totais / {odio} alertas.")

    print("✨ Sincronização Finalizada.")

if __name__ == "__main__":
    asyncio.run(sync_integrity())
