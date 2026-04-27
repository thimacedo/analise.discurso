import httpx
import asyncio
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configurações de Ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, RAPIDAPI_KEY]):
    print("ERRO: Variaveis de ambiente nao configuradas.")
    sys.exit(1)

def get_sb_headers():
    return {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

# --- ESTRATÉGIAS DE CARGA (LOAD BALANCER) ---

class APIStrategy:
    def __init__(self, host, name):
        self.host = host
        self.name = name
        self.is_active = True
        self.failure_count = 0
        self.cooldown_until = 0

    def mark_failure(self):
        self.failure_count += 1
        if self.failure_count >= 3:
            print(f"[!] CIRCUIT BREAKER: {self.name} em cooldown por 15 min.")
            self.is_active = False
            self.cooldown_until = time.time() + 900 # 15 min

    def check_health(self):
        if not self.is_active and time.time() > self.cooldown_until:
            self.is_active = True
            self.failure_count = 0
            print(f"[+] CIRCUIT BREAKER: {self.name} restaurada.")
        return self.is_active

class LoadBalancer:
    def __init__(self):
        self.strategies = [
            APIStrategy("instagram-scrapper-new.p.rapidapi.com", "Scraper-New"),
            APIStrategy("instagram-public-bulk-scraper.p.rapidapi.com", "Bulk-Scraper"),
            APIStrategy("instagram-scraper-20251.p.rapidapi.com", "Scraper-20251")
        ]
        self.current = 0

    def get_next(self):
        for _ in range(len(self.strategies)):
            strategy = self.strategies[self.current]
            self.current = (self.current + 1) % len(self.strategies)
            if strategy.check_health():
                return strategy
        return None

# --- MOTOR DE EXECUÇÃO ---

async def collect_target(client, target, strategy):
    username = target['username']
    c_db_id = target['id']
    
    print(f"[-] @{username} via {strategy.name}")
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": strategy.host,
        "Content-Type": "application/json"
    }

    try:
        # 1. Busca Feed
        # Nota: Adaptar o endpoint conforme a documentacao de cada API
        res = await client.post(f"https://{strategy.host}/getFeedByUsername", 
                                json={"username": username}, 
                                headers=headers, 
                                timeout=20.0)
        
        if res.status_code == 429:
            strategy.mark_failure()
            return

        posts = res.json().get('data', [])[:2]
        if not posts: return

        for post in posts:
            p_id = post.get('id')
            # 2. Busca Comentarios
            c_res = await client.post(f"https://{strategy.host}/getMediaComments", 
                                     json={"media_id": p_id}, 
                                     headers=headers)
            
            comments = c_res.json().get('comments', [])[:10]
            payload = [{
                "id_externo": str(c.get('id')),
                "candidato_id": c_db_id,
                "texto_bruto": c.get('text'),
                "autor_username": c.get('owner', {}).get('username'),
                "fonte_coleta": strategy.name,
                "raw_metadata": c
            } for c in comments]

            if payload:
                await client.post(f"{SUPABASE_URL}/rest/v1/comentarios", 
                                json=payload, 
                                headers={**get_sb_headers(), "Prefer": "resolution=merge-duplicates"})
        
        print(f"  [✓] @{username} Finalizado.")
        strategy.failure_count = 0 # Reset de falhas em caso de sucesso

    except Exception as e:
        print(f"  [!] Erro em @{username}: {str(e)[:40]}")
        strategy.mark_failure()

async def main():
    print("Sentinela Diamond v15.18.0 - Orquestrador Load-Balancer")
    lb = LoadBalancer()
    
    async with httpx.AsyncClient() as client:
        # Busca alvos ativos
        res = await client.get(f"{SUPABASE_URL}/rest/v1/candidatos?status_monitoramento=eq.Ativo&select=id,username", headers=get_sb_headers())
        targets = res.json()
        
        # Processamento em lotes de 6 (2 por API simultaneamente)
        batch_size = 6
        for i in range(0, len(targets), batch_size):
            batch = targets[i:i+batch_size]
            tasks = []
            for target in batch:
                strategy = lb.get_next()
                if strategy:
                    tasks.append(collect_target(client, target, strategy))
            
            if tasks:
                await asyncio.gather(*tasks)
                print(f"--- Lote {i//batch_size + 1} Concluido ---")
                await asyncio.sleep(5) # Cooldown entre lotes

if __name__ == "__main__":
    asyncio.run(main())
