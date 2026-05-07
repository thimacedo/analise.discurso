# core/session_manager.py
import json
import os
import logging
from typing import Optional, List, Dict
import random

class SessionManager:
    """Gerenciador de persistência e rotação de proxies (PSR-1 compliant)"""
    def __init__(self, session_dir: str = "sessions"):
        self.session_dir = session_dir
        self.logger = logging.getLogger("Sentinela.Session")
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)

    def save_session(self, profile_name: str, cookies: List[Dict]):
        """Salva os cookies da sessão em formato JSON."""
        file_path = os.path.join(self.session_dir, f"{profile_name}_cookies.json")
        try:
            with open(file_path, 'w') as f:
                json.dump(cookies, f)
            self.logger.info(f"Sessão salva para {profile_name}.")
        except Exception as e:
            self.logger.error(f"Erro ao salvar sessão: {e}")

    def load_session(self, profile_name: str) -> Optional[List[Dict]]:
        """Carrega os cookies salvos para um perfil."""
        file_path = os.path.join(self.session_dir, f"{profile_name}_cookies.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Erro ao carregar sessão {profile_name}: {e}")
        return None

    def get_proxy_config(self) -> Optional[Dict]:
        """Retorna a configuração de proxy para rotação."""
        proxies = [
            {"server": "http://proxy.exemplo.com:8080", "username": "user1", "password": "pass1"},
            None
        ]
        return random.choice(proxies)

    def validate_session(self, profile_name: str) -> bool:
        """Verifica se a sessão ainda é válida."""
        cookies = self.load_session(profile_name)
        return bool(cookies)
