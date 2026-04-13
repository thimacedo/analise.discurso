import json
import os
from datetime import datetime
from instagrapi import Client
from dotenv import load_dotenv

load_dotenv()

def sincronizar_perfis():
    username = os.getenv("IG_USERNAME")
    password = os.getenv("IG_PASSWORD")
    
    if not username or not password:
        print("❌ Credenciais não encontradas no .env")
        return

    print("--- Logando para buscar lista de seguidos ---")
    cl = Client()
    
    # Tenta carregar sessao salva
    if os.path.exists("session.json"):
        cl.load_settings("session.json")
    
    try:
        cl.login(username, password)
        cl.dump_settings("session.json")
        
        following = cl.user_following(cl.user_id)
        perfis = [user.username for user in following.values()]
        
        dados = {
            "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S") if os.name == 'nt' else os.popen('date').read(),
            "perfis": perfis
        }
        
        with open("perfis_monitorados.json", "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
            
        print(f"Pronto: {len(perfis)} perfis salvos em 'perfis_monitorados.json'")
        print("Dica: Voce ja pode fazer logout do Instagram se quiser seguranca extra.")
        
    except Exception as e:
        print(f"Erro ao buscar seguidos: {e}")

if __name__ == "__main__":
    sincronizar_perfis()