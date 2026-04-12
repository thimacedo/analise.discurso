import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

class AnalisadorPerfis:
    def __init__(self, cache_file="perfis_candidatos.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("⚠️ GEMINI_API_KEY não configurada. Análise de perfis desativada.")
            self.api_key = None
            return

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def analisar_perfil(self, username, bio, nome_completo):
        # Se já temos no cache, retornamos direto (gratuito e instantâneo)
        if username in self.cache:
            return self.cache[username]
        
        if not self.api_key:
            return self._dados_padrao(username)

        print(f"  🤖 Consultando IA gratuita para @{username}...")
        prompt = f"""Analise o perfil de um político/candidato brasileiro com base no nome e na biografia do Instagram.
        Nome: {nome_completo}
        Usuário: @{username}
        Biografia: {bio}

        Retorne APENAS um JSON válido (sem markdown, sem crases) com as seguintes chaves:
        - "cargo": O cargo que concorre ou exerce (ex: "Deputado Federal", "Prefeito", "Senador", "Nenhum"). Use "Nenhum" se não for político.
        - "sexo": "Masculino", "Feminino" ou "Indeterminado".
        - "raca": "Branco", "Preto", "Pardo", "Indígena", "Asiático" ou "Indeterminado". (Baseie-se em probabilidades contextuais ou no nome se não houver foto, default: "Indeterminado")
        - "estado": Sigla do estado (ex: "SP", "MG", "RJ") ou "N/A".
        - "partido": Sigla do partido (ex: "PL", "PT", "MDB") ou "N/A".
        - "ideologia": "Direita", "Centro-Direita", "Centro", "Centro-Esquerda", "Esquerda" ou "Indeterminado".
        - "pautas": Lista com as 3 principais pautas visíveis na bio (ex: ["Família", "Economia", "Saúde"]).

        JSON:"""

        try:
            # Chamada HTTP DIRETA (sem dependências pesadas)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 1024
                }
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            text_response = result['candidates'][0]['content']['parts'][0]['text'].strip()
            
            # Limpeza de segurança (caso a IA coloque crases do markdown)
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            
            dados = json.loads(text_response.strip())
            
            # Garantir que todas as chaves existem
            dados_padrao = self._dados_padrao(username)
            dados_padrao.update(dados)
            dados_padrao['username'] = username
            
            self.cache[username] = dados_padrao
            self._save_cache()
            
            # Pausa de segurança para não estourar cota gratuita (15 req/min)
            time.sleep(4.5) 
            return dados_padrao

        except Exception as e:
            print(f"  ⚠️ Erro na IA para @{username}: {e}")
            return self._dados_padrao(username)

    def _dados_padrao(self, username):
        return {
            "username": username,
            "cargo": "Indeterminado",
            "sexo": "Indeterminado",
            "raca": "Indeterminado",
            "estado": "N/A",
            "partido": "N/A",
            "ideologia": "Indeterminado",
            "pautas": []
        }