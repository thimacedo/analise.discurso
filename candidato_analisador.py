import os
import json
import time
import instaloader
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AnalisadorPerfis:
    def __init__(self, cache_file="perfis_candidatos.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ GEMINI_API_KEY não configurada. Análise de perfis desativada.")
            self.model = None
            return
        
        try:
            genai.configure(api_key=api_key)
            # Usando o modelo Flash (100% gratuito e rápido)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            print(f"❌ Erro ao inicializar Gemini: {e}")
            self.model = None

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
        
        if not self.model:
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
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            
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

    def obter_bio_perfil(self, username):
        """Obtém a bio via instaloader anônimo"""
        try:
            L = instaloader.Instaloader(download_pictures=False, save_metadata=False)
            profile = instaloader.Profile.from_username(L.context, username)
            return {
                "nome_completo": profile.full_name,
                "bio": profile.biography
            }
        except Exception as e:
            print(f"  ⚠️ Não foi possível obter bio de @{username}: {e}")
            return {"nome_completo": "", "bio": ""}

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
