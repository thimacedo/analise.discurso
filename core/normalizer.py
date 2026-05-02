import os
from typing import List, Optional, Dict
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class TargetNormalizer:
    """
    Normaliza nomes genéricos de alvos para usernames oficiais do Instagram.
    """
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        if not self.supabase_url or not self.supabase_key:
            print("⚠️ [TargetNormalizer] Credenciais Supabase não encontradas.")
            self.client = None
        else:
            self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
        self._cache_usernames: Dict[str, str] = {}
        self._profiles_loaded = False

    def _load_all_profiles(self):
        """Carrega perfis em memória para matching rápido."""
        if not self.client or self._profiles_loaded:
            return

        try:
            # Busca campos relevantes para matching
            response = self.client.table('candidatos').select('username, nome, apelido').execute()
            for item in response.data:
                username = item.get('username', '').lower().strip()
                nome = item.get('nome', '').lower().strip()
                apelido = item.get('apelido', '').lower().strip()

                if username:
                    # Mapeia nome e apelido para o username
                    if nome: self._cache_usernames[nome] = username
                    if apelido: self._cache_usernames[apelido] = username
                    # Mapeia o próprio username para garantir consistência
                    self._cache_usernames[username] = username
            
            self._profiles_loaded = True
            print(f"✅ [TargetNormalizer] {len(self._cache_usernames)} mapeamentos carregados em memória.")
        except Exception as e:
            print(f"❌ [TargetNormalizer] Erro ao carregar perfis: {e}")

    def normalize(self, target: str) -> str:
        """
        Tenta encontrar o username oficial para um nome/apelido.
        Retorna o alvo original se não encontrar correspondência.
        """
        if not target:
            return ""

        target_clean = target.lower().strip()
        
        # Garante que os perfis estão carregados
        self._load_all_profiles()

        # Busca exata no cache (que contém nomes, apelidos e usernames)
        normalized = self._cache_usernames.get(target_clean)
        
        if normalized:
            if normalized != target_clean:
                print(f"🔄 [Normalizer] Traduzido: '{target}' -> @{normalized}")
            return normalized

        # Se não encontrou, retorna o original (pode já ser um username novo não cadastrado)
        return target_clean

    def normalize_list(self, targets: List[str]) -> List[str]:
        """Normaliza uma lista de alvos."""
        return list(dict.fromkeys([self.normalize(t) for t in targets if t]))

# Instância única global
target_normalizer = TargetNormalizer()
