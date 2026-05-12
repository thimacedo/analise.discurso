
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def check_backlog():
    headers = {
        "apikey": os.getenv("SUPABASE_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
    }
    url = os.getenv("SUPABASE_URL")
    
    async with httpx.AsyncClient() as client:
        # 1. Perfis Totais vs Ativos
        r_perfis = await client.get(f"{url}/rest/v1/candidatos?select=username,status_monitoramento", headers=headers)
        perfis = r_perfis.json() if r_perfis.status_code == 200 else []
        ativos = [p for p in perfis if p.get('status_monitoramento') == 'ATIVO']
        
        # 2. Comentários Totais
        r_total = await client.get(f"{url}/rest/v1/comentarios?select=id", headers=headers)
        total_comentarios = len(r_total.json()) if r_total.status_code == 200 else 0
        
        # 3. Pendentes de IA (já temos do health check, mas para consolidar)
        r_ia = await client.get(f"{url}/rest/v1/comentarios?processado_ia=eq.false&select=id", headers=headers)
        pendentes_ia = len(r_ia.json()) if r_ia.status_code == 200 else 0

        print(f"\n--- RELATÓRIO DE BACKLOG ---")
        print(f"👤 Perfis Monitorados: {len(perfis)}")
        print(f"🟢 Perfis em Monitoramento Ativo: {len(ativos)}")
        print(f"💬 Volume Total de Comentários: {total_comentarios}")
        print(f"🧠 Comentários Aguardando IA: {pendentes_ia}")
        print(f"----------------------------\n")

if __name__ == "__main__":
    asyncio.run(check_backlog())
