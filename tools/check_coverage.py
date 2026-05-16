import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def check_coverage():
    headers = {
        "apikey": os.getenv("SUPABASE_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}"
    }
    url = os.getenv("SUPABASE_URL")
    
    async with httpx.AsyncClient() as client:
        # 1. Busca todos os candidatos ativos
        r_candidatos = await client.get(f"{url}/rest/v1/candidatos?select=username", headers=headers)
        todos_usernames = {p['username'] for p in r_candidatos.json()} if r_candidatos.status_code == 200 else set()
        
        # 2. Busca usernames que já possuem comentários
        # Usamos uma query que pega os IDs dos candidatos que aparecem na tabela de comentários
        r_comentados = await client.get(f"{url}/rest/v1/comentarios?select=candidato_id", headers=headers)
        usernames_com_dados = {c['candidato_id'] for c in r_comentados.json() if c.get('candidato_id')} if r_comentados.status_code == 200 else set()
        
        # 3. Calcula a diferença
        nao_monitorados = todos_usernames - usernames_com_dados
        
        print(f"\n--- ANÁLISE DE COBERTURA ---")
        print(f"Total de Perfis: {len(todos_usernames)}")
        print(f"Perfis com Dados: {len(usernames_com_dados)}")
        print(f"Perfis SEM NENHUM dado: {len(nao_monitorados)}")
        
        if nao_monitorados:
            print(f"\nExemplos de perfis ainda não tocados:")
            for p in list(nao_monitorados)[:15]:
                print(f" - @{p}")
            if len(nao_monitorados) > 15:
                print(f" ... e mais {len(nao_monitorados)-15} perfis.")
        print(f"----------------------------\n")

if __name__ == "__main__":
    asyncio.run(check_coverage())
