import httpx
import json
import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SGAICollector:
    def __init__(self):
        self.api_key = os.getenv("SGAI_API_KEY", "sgai-a3b1dbb2-e7ee-4b0a-a167-7d83d740f138")
        self.base_url = "https://v2-api.scrapegraphai.com/api/extract"
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.headers = {
            "SGAI-APIKEY": self.api_key,
            "Content-Type": "application/json"
        }

    async def get_alvos(self):
        h = {"apikey": self.supabase_key, "Authorization": f"Bearer {self.supabase_key}"}
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.supabase_url}/rest/v1/candidatos?status_monitoramento=ilike.Ativo", headers=h)
            return r.json() if r.status_code == 200 else []

    async def extrair_comentarios(self, username):
        print(f"🚀 [MIRROR] Analisando @{username}...")
        
        # Picuki: Rota direta de post para evitar navegação complexa
        target_url = f"https://www.picuki.com/profile/{username}"
        
        payload = {
            "url": target_url,
            "prompt": "List the last 5 user comments shown on this page. Each item should have 'text' and 'username'. Return as JSON list under key 'comments'."
        }
        
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                res = await client.post(self.base_url, headers=self.headers, json=payload)
                if res.status_code == 200:
                    data = res.json().get('json', {})
                    return data.get('comments', [])
                print(f"❌ Status {res.status_code} para @{username}")
        except Exception as e:
            print(f"⚠️ Timeout/Erro @{username}")
        return []

    async def salvar_comentarios(self, username, comentarios):
        if not comentarios: return
        h = {"apikey": self.supabase_key, "Authorization": f"Bearer {self.supabase_key}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
        preparados = []
        for c in comentarios:
            texto = str(c.get('text', '')).strip()
            if len(texto) < 4: continue
            preparados.append({
                "candidato_id": username,
                "texto_bruto": texto,
                "autor": c.get('username', 'anonimo'),
                "data_coleta": datetime.now().isoformat(),
                "processado_ia": False,
                "is_hate": False
            })
            
        if preparados:
            async with httpx.AsyncClient() as client:
                await client.post(f"{self.supabase_url}/rest/v1/comentarios", headers=h, json=preparados)
                await client.patch(f"{self.supabase_url}/rest/v1/candidatos?username=eq.{username}", headers=h, json={"atualizado_em": datetime.now().isoformat()})
            print(f"✅ {len(preparados)} evidências reais salvas para @{username}")

    async def run(self):
        alvos = await self.get_alvos()
        # Sort prioritário para o teste
        tops = ["lulaoficial", "jairmessiasbolsonaro", "nikolasferreirainfo"]
        alvos_ordenados = [a for a in alvos if a['username'] in tops] + [a for a in alvos if a['username'] not in tops]
        
        for alvo in alvos_ordenados[:5]:
            await self.extrair_comentarios(alvo['username']) # Log interno já salva
            # Nota: O método salvar_comentarios precisa ser chamado
            un = alvo['username']
            comms = await self.extrair_comentarios(un)
            await self.salvar_comentarios(un, comms)
            time.sleep(5)

if __name__ == "__main__":
    import asyncio
    asyncio.run(SGAICollector().run())
