import os
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

class TargetManager:
    def __init__(self, hours_threshold=24):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.threshold = hours_threshold
        self.recently_scraped = set()
        self._load_recent_profiles()

    def _load_recent_profiles(self):
        """Busca no banco UMA VEZ os perfis atualizados recentemente e guarda em memória."""
        cutoff_time = (datetime.utcnow() - timedelta(hours=self.threshold)).isoformat()
        
        try:
            # Usando a tabela 'candidatos' conforme pipelines.py
            response = self.supabase.table('candidatos') \
                .select('username') \
                .gte('last_scraped_at', cutoff_time) \
                .execute()
            
            # Se chegamos aqui, a coluna existe
            self.recently_scraped = {item['username'] for item in response.data}
            print(f"📊 [TargetManager] {len(self.recently_scraped)} perfis já atualizados nas últimas {self.threshold}h. Serão ignorados.")
            
        except Exception as e:
            # Se a coluna não existe, apenas avisamos e não filtramos
            if "column" in str(e) and "does not exist" in str(e):
                print(f"⚠️ [TargetManager] Coluna 'last_scraped_at' não encontrada. Filtro desativado até a migração SQL.")
            else:
                print(f"⚠️ [TargetManager] Erro ao buscar perfis recentes: {e}")
            self.recently_scraped = set()

    def filter_targets(self, target_list):
        """
        Recebe a lista de alvos (usernames ou objetos com 'username') e retorna apenas os que precisam ser raspados.
        """
        if not target_list:
            return []

        # Normaliza para lista de strings se for lista de objetos
        normalized_list = []
        for t in target_list:
            if isinstance(t, dict):
                normalized_list.append(t.get('username'))
            else:
                normalized_list.append(str(t))

        # Remove duplicatas e nulos
        unique_targets = list(set(filter(None, normalized_list)))
        
        # Filtra os que já foram raspados recentemente
        targets_to_scrape = [
            u for u in unique_targets 
            if u not in self.recently_scraped
        ]
        
        ignored_count = len(unique_targets) - len(targets_to_scrape)
        print(f"🎯 [TargetManager] {len(unique_targets)} alvos solicitados. {len(targets_to_scrape)} para raspagem. ({ignored_count} ignorados)")
        
        return targets_to_scrape
