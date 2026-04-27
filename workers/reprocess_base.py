import os
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")

def get_sb_headers():
    return {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

async def reprocess_base():
    print("🔬 Iniciando Deep Forensic Scan (Reprocessamento Geral)...")
    
    # Dicionario Expandido PASA v16.4
    keywords = [
        "ladrao", "corrupto", "ditador", "genocida", "assassino", "safado", "vagabundo",
        "comunista", "fascista", "nazista", "verme", "rato", "lixo", "escoria", "jumento",
        "gado", "mortadela", "ditadura", "golpe", "fraude", "urnas", "xandao", "careca",
        "miliante", "quadrilha", "propina", "desvio", "condenado"
    ]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Busca TODOS os registros da base
        res = await client.get(f"{URL}/rest/v1/comentarios?select=id,texto_bruto", headers=get_sb_headers())
        base = res.json()
        
        print(f"[-] Analisando {len(base)} registros com Matriz v16.4...")
        
        hits = 0
        for i in range(0, len(base), 50): # Lotes de 50 para estabilidade
            batch = base[i:i+50]
            
            for item in batch:
                texto = str(item.get('texto_bruto', '')).lower()
                is_hate = any(k in texto for k in keywords)
                
                if is_hate: hits += 1
                
                # PATCH Seguro
                await client.patch(
                    f"{URL}/rest/v1/comentarios?id=eq.{item['id']}",
                    json={"processado_ia": True, "is_hate": is_hate},
                    headers=get_sb_headers()
                )
            
            print(f"  [>] Lote {i//50 + 1} concluido. Alertas acumulados: {hits}")

        print(f"✅ REPROCESSAMENTO FINALIZADO. Total de Alertas: {hits}")

if __name__ == "__main__":
    asyncio.run(reprocess_base())
