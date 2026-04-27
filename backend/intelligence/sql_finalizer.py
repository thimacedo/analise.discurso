import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_sb_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

async def run_sql_finalization():
    print("⚡ Operacao de Choque: Finalizacao via SQL Direto")
    
    # Lista de palavras de hostilidade para classificacao interna
    keywords = ["ladrao", "corrupto", "ditador", "genocida", "assassino", "safado", "vagabundo"]
    pattern = "|".join(keywords)
    
    # Como nao temos acesso ao SQL Editor, vamos fazer via PATCH registro a registro (Estrategia Segura)
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Busca IDs pendentes
        res = await client.get(f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.false&select=id,texto_bruto", headers=get_sb_headers())
        pending = res.json()
        
        print(f"[-] Registros pendentes localizados: {len(pending)}")
        
        for item in pending[:200]: # Processa 200 para dar folego ao Dashboard
            is_hate = any(k in str(item['texto_bruto']).lower() for k in keywords)
            
            # PATCH: Atualiza APENAS as colunas desejadas sem violar o ID_EXTERNO
            await client.patch(
                f"{SUPABASE_URL}/rest/v1/comentarios?id=eq.{item['id']}",
                json={"processado_ia": True, "is_hate": is_hate},
                headers=get_sb_headers()
            )
        
        print("✅ Operacao Parcial Concluida. Dashboard atualizado.")

if __name__ == "__main__":
    asyncio.run(run_sql_finalization())
