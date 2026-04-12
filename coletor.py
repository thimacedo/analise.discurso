import os
import time
import random
import requests
import pandas as pd
from datetime import datetime
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ClientThrottledError, RateLimitError, ChallengeRequired
from dotenv import load_dotenv

load_dotenv()

class ColetorSeguro:
    def __init__(self, session_file="session.json"):
        self.client = Client()
        self.session_file = session_file
        self.username = os.getenv("IG_USERNAME")
        self.password = os.getenv("IG_PASSWORD")
        if not self.username or not self.password:
            raise ValueError("IG_USERNAME ou IG_PASSWORD não configurados.")

    def log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Coletor] {msg}")

    def login(self):
        if os.path.exists(self.session_file):
            try:
                self.client.load_settings(self.session_file)
                self.client.get_timeline_feed()
                self.log("✅ Sessão carregada com sucesso.")
                return
            except Exception:
                self.log("⚠️ Sessão expirada. Tentando novo login...")
        try:
            self.client.login(self.username, self.password)
            self.client.dump_settings(self.session_file)
            self.log("✅ Novo login realizado e sessão salva.")
        except ChallengeRequired as e:
            self.log("⚠️ Instagram requer desafio/2FA. Digite o código (se for 2FA) ou resolva o desafio no app.")
            # Se for 2FA, a mensagem pode indicar; neste caso, pedimos o código
            # A instagrapi lida com 2FA automaticamente se você passar verification_code
            # Vamos pedir o código e tentar novamente:
            code = input("Digite o código de autenticação (2FA): ")
            self.client.login(self.username, self.password, verification_code=code)
            self.client.dump_settings(self.session_file)
            self.log("✅ Login com 2FA realizado.")
        except Exception as e:
            if "Two-factor authentication required" in str(e):
                code = input("⚠️ Digite o código de 2FA: ")
                self.client.login(self.username, self.password, verification_code=code)
                self.client.dump_settings(self.session_file)
                self.log("✅ Login com 2FA realizado.")
            else:
                raise e

    # ... (restante do coletor permanece igual)