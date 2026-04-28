import httpx
import json
import os
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SGAICollector:
    def __init__(self):
        self.api_key = os.getenv("SGAI_API_KEY", "sgai-a3b1dbb2-e7ee-4b0a-a167-7d83d740f138")
        self.base_url = "https://v2-api.scrapegraphai.com/api/extract"
        self.supabase_url = "https://vhamejkldzxbeibqeqpk.supabase.co"
        self.supabase_key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY")
        self.headers = {
            "SGAI-APIKEY": self.api_key,
            "Content-Type": "application/json"
        }

    async def get_alvos(self):
        h = {"apikey": self.supabase_key, "Authorization": f"Bearer {self.supabase_key}"}
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.supabase_url}/rest/v1/candidatos?status_monitoramento=eq.Ativo&select=id,username", headers=h)
            return r.json() if r.status_code == 200 else []

    async def extrair_comentarios(self, username):
        print(f"🚀 [SGAI] Extraindo @{username} via Picuki...")
        payload = {
            "url": f"https://www.picuki.com/profile/{username}",
            "prompt": "Extract the most recent 10 comments. Return a JSON list of objects with 'text' and 'username' keys under the root key 'comments'."
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                res = await client.post(self.base_url, headers=self.headers, json=payload)
                if res.status_code == 200:
                    return res.json().get('json', {}).get('comments', [])
                print(f"⚠️ Status {res.status_code} para @{username}")
        except Exception as e:
            print(f"❌ Erro na extração @{username}: {e}")
        return []

    async def salvar(self, candidato_id, username, comentarios):
        if not comentarios: return
        h = {"apikey": self.supabase_key, "Authorization": f"Bearer {self.supabase_key}", "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates"}
        payload = [{
            "candidato_id": candidato_id,
            "texto_bruto": c.get('text', ''),
            "autor_username": c.get('username', 'anonimo'),
            "fonte_coleta": "SGAI/Picuki",
            "processado_ia": False
        } for c in comentarios if len(str(c.get('text', ''))) > 3]

        if payload:
            async with httpx.AsyncClient() as client:
                r = await client.post(f"{self.supabase_url}/rest/v1/comentarios", headers=h, json=payload)
                print(f"✅ {len(payload)} evidências salvas para @{username} (Status: {r.status_code})")

    async def run(self):
        alvos = await self.get_alvos()
        print(f"📍 Monitorando {len(alvos)} alvos ativos.")
        for alvo in alvos[:10]: # Lote inicial para persistência técnica
            comms = await self.extrair_comentarios(alvo['username'])
            await self.salvar(alvo['id'], alvo['username'], comms)
            await asyncio.sleep(2)

if __name__ == '__main__':
    asyncio.run(SGAICollector().run())
