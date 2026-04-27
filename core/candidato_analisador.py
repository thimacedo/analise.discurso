import os
import json
import time
import instaloader
from google import genai
from dotenv import load_dotenv

load_dotenv()

class AnalisadorPerfis:
    def __init__(self, cache_file="perfis_candidatos.json"):
        self.cache_file = cache_file
        self.cache = self._load_cache()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Aviso: GEMINI_API_KEY nao configurada. Analise de perfis desativada.")
            self.client = None
            return
        
        try:
            # Nova forma de autenticar o Google GenAI (SDK Moderno)
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"Erro ao inicializar Gemini: {e}")
            self.client = None

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)

    def analisar_perfil(self, username, bio, nome_completo):
        if username in self.cache:
            return self.cache[username]
        
        if not self.client:
            return self._dados_padrao(username)

        print(f"  Consultando IA para @{username}...")
        prompt = f"""Analise o perfil de um politico/candidato brasileiro com base no nome e na biografia do Instagram.
        Nome: {nome_completo}
        Usuario: @{username}
        Biografia: {bio}

        Retorne APENAS um JSON valido (sem markdown, sem crases) com as seguintes chaves:
        - "cargo": O cargo que concorre ou exerce (ex: "Deputado Federal", "Prefeito", "Senador", "Nenhum"). Use "Nenhum" se nao for politico.
        - "sexo": "Masculino", "Feminino" ou "Indeterminado".
        - "raca": "Branco", "Preto", "Pardo", "Indigena", "Asiatico" ou "Indeterminado".
        - "estado": Sigla do estado (ex: "SP", "MG", "RJ") ou "N/A".
        - "partido": Sigla do partido (ex: "PL", "PT", "MDB") ou "N/A".
        - "ideologia": "Direita", "Centro-Direita", "Centro", "Centro-Esquerda", "Esquerda" ou "Indeterminado".
        - "pautas": Lista com as 3 principais pautas visiveis na bio (ex: ["Familia", "Economia", "Saude"]).

        JSON:"""

        try:
            # Nova sintaxe da API do Google
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt
            )
            text_response = response.text.strip()
            
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            
            dados = json.loads(text_response.strip())
            
            dados_padrao = self._dados_padrao(username)
            dados_padrao.update(dados)
            dados_padrao['username'] = username
            
            self.cache[username] = dados_padrao
            self._save_cache()
            
            time.sleep(4.5) 
            return dados_padrao

        except Exception as e:
            print(f"  Erro na IA para @{username}: {e}")
            return self._dados_padrao(username)

    def obter_bio_perfil(self, username):
        """Obtem a bio via instaloader usando a SESSAO LOGADA para evitar 403"""
        try:
            L = instaloader.Instaloader(download_pictures=False, save_metadata=False)
            
            # CARREGA A SESSAO
            session_file = "session.json"
            ig_username = os.getenv("IG_USERNAME")
            if os.path.exists(session_file) and ig_username:
                L.load_session(ig_username, L.context._load_json(session_file))
            
            profile = instaloader.Profile.from_username(L.context, username)
            return {
                "nome_completo": profile.full_name,
                "bio": profile.biography
            }
        except Exception as e:
            print(f"  Aviso: Nao foi possivel obter bio de @{username}: {e}")
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
