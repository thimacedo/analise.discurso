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
        """Carrega perfis em memória com priorização inteligente."""
        if not self.client or self._profiles_loaded:
            return

        try:
            # Busca campos reais encontrados via inspeção
            # Ordenamos por seguidores desc para que o mais importante ganhe no mapeamento simples
            response = self.client.table('candidatos') \
                .select('username, nome_completo, seguidores') \
                .order('seguidores', desc=True) \
                .execute()
            
            for item in response.data:
                username = str(item.get('username', '')).lower().strip()
                nome_completo = str(item.get('nome_completo', '')).lower().strip()

                if username:
                    # Mapeia nome_completo para o username (prioridade alta)
                    if nome_completo and nome_completo != 'none': 
                        self._cache_usernames[nome_completo] = username
                    
                    # Tenta extrair primeiro nome e sobrenome
                    # Como está ordenado por seguidores, "Lula" vai mapear para o maior perfil que tem "Lula" no nome
                    partes_nome = nome_completo.split()
                    if partes_nome:
                        primeiro_nome = partes_nome[0]
                        ultimo_nome = partes_nome[-1]
                        
                        # Apenas mapeia se ainda não existir (garante que o com mais seguidores vença)
                        if primeiro_nome not in self._cache_usernames:
                            self._cache_usernames[primeiro_nome] = username
                        if ultimo_nome not in self._cache_usernames:
                            self._cache_usernames[ultimo_nome] = username

                    # Mapeia o próprio username (sempre vence se for exato)
                    self._cache_usernames[username] = username
            
            self._profiles_loaded = True
            print(f"✅ [TargetNormalizer] {len(self._cache_usernames)} mapeamentos carregados em memória (ordenados por relevância).")
        except Exception as e:
            print(f"❌ [TargetNormalizer] Erro ao carregar perfis: {e}")

    def normalize(self, target: str) -> str:
        """
        Tenta encontrar o username oficial para um nome/apelido.
        Retorna o alvo original se não encontrar correspondência.
        """
        if not target:
            return ""

        target_clean = str(target).lower().strip()
        
        # Garante que os perfis estão carregados
        self._load_all_profiles()

        # Busca exata no cache
        normalized = self._cache_usernames.get(target_clean)
        
        if normalized:
            if normalized != target_clean:
                print(f"🔄 [Normalizer] Traduzido: '{target}' -> @{normalized}")
            return normalized

        # Se não encontrou, retorna o original (pode já ser um username novo não cadastrado)
        return target_clean

    def normalize_list(self, targets: List[str]) -> List[str]:
        """Normaliza uma lista de alvos."""
        # Usa dict.fromkeys para manter ordem e remover duplicatas
        return list(dict.fromkeys([self.normalize(t) for t in targets if t]))

# Instância única global
target_normalizer = TargetNormalizer()
