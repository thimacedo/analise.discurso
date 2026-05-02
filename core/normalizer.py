import os
import unicodedata
from typing import List, Dict
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class TargetNormalizer:
    """Normaliza nomes genéricos de alvos para usernames do Instagram."""
    
    def __init__(self):
        self.client: Client = self._init_client()
        self._cache: Dict[str, str] = {}
        self._loaded = False

    def _init_client(self) -> Client:
        url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
        return create_client(url, key) if url and key else None

    def _clean(self, text: str) -> str:
        if not text or str(text).lower() == 'none': return ""
        return unicodedata.normalize('NFKC', str(text)).lower().strip()

    def _load(self):
        if not self.client or self._loaded: return

        try:
            resp = self.client.table('candidatos') \
                .select('username, nome_completo, seguidores') \
                .order('seguidores', desc=True).execute()
            
            for item in resp.data:
                user = self._clean(item.get('username'))
                nome = self._clean(item.get('nome_completo'))
                if not user: continue

                self._cache[user] = user
                if nome and len(nome) > 3:
                    self._cache.setdefault(nome, user)
                    for p in nome.split():
                        if len(p) > 3: self._cache.setdefault(p, user)
            
            self._loaded = True
            print(f"✅ [Normalizer] {len(self._cache)} perfis mapeados.")
        except Exception as e:
            print(f"❌ [Normalizer] Falha no carregamento: {e}")

    def normalize(self, target: str) -> str:
        if not target: return ""
        self._load()
        clean_target = self._clean(target)
        normalized = self._cache.get(clean_target, clean_target)
        if normalized != clean_target:
            print(f"🔄 [Normalizer] '{target}' -> @{normalized}")
        return normalized

    def normalize_list(self, targets: List[str]) -> List[str]:
        return list(dict.fromkeys(self.normalize(t) for t in targets if t))

target_normalizer = TargetNormalizer()
