import httpx, os, asyncio
from dotenv import load_dotenv
load_dotenv()

async def main():
    h = {"apikey": os.getenv("SUPABASE_KEY"), "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"}
    async with httpx.AsyncClient() as client:
        # 1. Verificar Backlog de IA
        r_ia = await client.get(f"{os.getenv('SUPABASE_URL')}/rest/v1/comentarios?processado_ia=eq.false&select=id", headers=h)
        pendentes = len(r_ia.json()) if r_ia.status_code == 200 else "Erro"
        
        # 2. Verificar Alertas Reais
        r_alerts = await client.get(f"{os.getenv('SUPABASE_URL')}/rest/v1/comentarios?is_hate=eq.true&select=id", headers=h)
        alertas = len(r_alerts.json()) if r_alerts.status_code == 200 else "Erro"
        
        print(f"--- STATUS DO SISTEMA ---")
        print(f"📦 Comentários Pendentes (IA): {pendentes}")
        print(f"🚨 Alertas de Ódio Detectados: {alertas}")
        print(f"-------------------------")

if __name__ == "__main__":
    asyncio.run(main())
