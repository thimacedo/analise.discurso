import httpx
import time
import os
import json
from datetime import datetime

# Configurações do Ambiente
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "d0f8b83ba1msh27e35d3d042e3afp134bb9jsnd112e08fb6b8")
RAPIDAPI_HOST = "instagram-scrapper-new.p.rapidapi.com"

class RapidInstaCollector:
    def __init__(self):
        self.rapid_client = httpx.Client(
            headers={
                "x-rapidapi-host": RAPIDAPI_HOST,
                "x-rapidapi-key": RAPIDAPI_KEY,
                "Content-Type": "application/json"
            },
            timeout=30.0
        )

    def get_feed_by_username(self, username):
        """Tenta o endpoint mais comum de busca de feed por username"""
        url = f"https://{RAPIDAPI_HOST}/getFeedByUsername" 
        try:
            response = self.rapid_client.post(url, json={"username": username})
            if response.status_code == 404: # Tenta GET se POST falhar
                response = self.rapid_client.get(url, params={"username": username})
            
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])[:3]
        except Exception as e:
            print(f"  [DEBUG] Falha no endpoint /getFeedByUsername: {e}")
            return []

    def get_feed_by_hashtag(self, tag):
        """Endpoint de hashtag legado (mencionado no seu código original)"""
        url = f"https://{RAPIDAPI_HOST}/getFeedByHashtagLegacy"
        try:
            response = self.rapid_client.post(url, json={"tag": tag})
            response.raise_for_status()
            return response.json().get('data', [])[:3]
        except Exception as e:
            print(f"  [DEBUG] Falha no endpoint /getFeedByHashtagLegacy: {e}")
            return []

if __name__ == "__main__":
    collector = RapidInstaCollector()
    
    print(f"🚀 Iniciando Diagnóstico de Endpoints")
    
    # Teste 1: Username
    print("--- Testando Busca por Username (@allysonbezerra.rn) ---")
    posts = collector.get_feed_by_username("allysonbezerra.rn")
    if posts:
        print(f"  ✅ Sucesso! Encontrados {len(posts)} posts.")
    else:
        # Teste 2: Hashtag
        print("--- Testando Busca por Hashtag (#parnamirim) ---")
        posts = collector.get_feed_by_hashtag("parnamirim")
        if posts:
            print(f"  ✅ Sucesso via Hashtag! Encontrados {len(posts)} posts.")
        else:
            print("  ❌ Ambos os endpoints falharam ou retornaram vazio.")

