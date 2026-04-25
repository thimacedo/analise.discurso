import os
import json
import requests
import time

# Configurações do Supabase
SUPABASE_URL = "https://vhamejkldzxbeibqeqpk.supabase.co"
SUPABASE_KEY = os.environ.get("SENTINELA_SUPABASE_KEY", "SUPABASE_KEY_PLACEHOLDER")
HEADERS = { "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json" }

# Lista Consolidada (Judiciário, Governadores e Deputados Influentes)
NEW_PROFILES = [
    # JUDICIÁRIO E CONTROLE
    {"username": "stf_oficial", "full_name": "Supremo Tribunal Federal", "cargo": "Institucional", "estado": "DF"},
    {"username": "tsejus", "full_name": "Tribunal Superior Eleitoral", "cargo": "Institucional", "estado": "DF"},
    {"username": "alexandre", "full_name": "Alexandre de Moraes", "cargo": "Ministro STF", "estado": "DF"},
    {"username": "gilmarmendes", "full_name": "Gilmar Mendes", "cargo": "Ministro STF", "estado": "DF"},
    {"username": "andrelmendoncaj", "full_name": "André Mendonça", "cargo": "Ministro STF", "estado": "DF"},
    {"username": "kassionunesmarques", "full_name": "Kássio Nunes Marques", "cargo": "Ministro STF", "estado": "DF"},
    {"username": "tcuoficial", "full_name": "Tribunal de Contas da União", "cargo": "Institucional", "estado": "DF"},
    {"username": "cguoficial", "full_name": "Controladoria-Geral da União", "cargo": "Institucional", "estado": "DF"},
    
    # GOVERNADORES (Amostra principal)
    {"username": "tarcisiogdf", "full_name": "Tarcísio de Freitas", "cargo": "Governador", "estado": "SP"},
    {"username": "romeuzemaoficial", "full_name": "Romeu Zema", "cargo": "Governador", "estado": "MG"},
    {"username": "helderbarbalho", "full_name": "Helder Barbalho", "cargo": "Governador", "estado": "PA"},
    {"username": "eduardoleite45", "full_name": "Eduardo Leite", "cargo": "Governador", "estado": "RS"},
    {"username": "raquellyraoficial", "full_name": "Raquel Lyra", "cargo": "Governadora", "estado": "PE"},
    {"username": "fatimabezerra13", "full_name": "Fátima Bezerra", "cargo": "Governadora", "estado": "RN"},
    {"username": "jeronimorodriguesba", "full_name": "Jerônimo Rodrigues", "cargo": "Governador", "estado": "BA"},
    {"username": "claud Castro", "full_name": "Cláudio Castro", "cargo": "Governador", "estado": "RJ"},
    {"username": "rinhonader", "full_name": "Ratinho Júnior", "cargo": "Governador", "estado": "PR"},
    {"username": "mauromendesoficial", "full_name": "Mauro Mendes", "cargo": "Governador", "estado": "MT"},

    # DEPUTADOS E INFLUENTES
    {"username": "nikolasferreiradm", "full_name": "Nikolas Ferreira", "cargo": "Deputado Federal", "estado": "MG"},
    {"username": "carla.zambelli", "full_name": "Carla Zambelli", "cargo": "Deputada Federal", "estado": "SP"},
    {"username": "guilherme_boulos", "full_name": "Guilherme Boulos", "cargo": "Deputado Federal", "estado": "SP"},
    {"username": "tabataamaralsp", "full_name": "Tabata Amaral", "cargo": "Deputada Federal", "estado": "SP"},
    {"username": "kimkataguiri", "full_name": "Kim Kataguiri", "cargo": "Deputado Federal", "estado": "SP"},
    {"username": "gleisihoffmann", "full_name": "Gleisi Hoffmann", "cargo": "Deputada Federal", "estado": "PR"},
    {"username": "janoneresreal", "full_name": "André Janones", "cargo": "Deputado Federal", "estado": "MG"},
    {"username": "eduardobolsonaro", "full_name": "Eduardo Bolsonaro", "cargo": "Deputado Federal", "estado": "SP"},
    {"username": "flaviobolsonaro", "full_name": "Flávio Bolsonaro", "cargo": "Senador", "estado": "RJ"},
    {"username": "marcelovanhattem", "full_name": "Marcel van Hattem", "cargo": "Deputado Federal", "estado": "RS"},
    {"username": "biakicis", "full_name": "Bia Kicis", "cargo": "Deputada Federal", "estado": "DF"},
    {"username": "sargentofahuroficial", "full_name": "Sargento Fahur", "cargo": "Deputado Federal", "estado": "PR"},
    {"username": "lucaspavanato", "full_name": "Lucas Pavanato", "cargo": "Vereador/Influencer", "estado": "SP"},
    {"username": "deltandallagnol", "full_name": "Deltan Dallagnol", "cargo": "Influenciador Político", "estado": "PR"},
    {"username": "magnomalta", "full_name": "Magno Malta", "cargo": "Senador", "estado": "ES"},
    {"username": "sergiomorooficial", "full_name": "Sergio Moro", "cargo": "Senador", "estado": "PR"},
    {"username": "carlosbolsonaro", "full_name": "Carlos Bolsonaro", "cargo": "Vereador", "estado": "RJ"}
]

def sync_to_supabase():
    print(f"🔄 Sincronizando {len(NEW_PROFILES)} perfis para o banco...")
    for p in NEW_PROFILES:
        # Tenta inserir na tabela 'candidatos'
        data = {
            "username": p['username'],
            "nome_completo": p['full_name'],
            "cargo": p['cargo'],
            "estado": p['estado'],
            "status_monitoramento": "Ativo"
        }
        url = f"{SUPABASE_URL}/rest/v1/candidatos"
        # Upsert baseado no username
        headers_upsert = HEADERS.copy()
        headers_upsert["Prefer"] = "resolution=merge-duplicates"
        res = requests.post(url, headers=headers_upsert, json=data)
        if res.status_code in [200, 201]:
            print(f" ✅ @{p['username']} sincronizado.")
        else:
            print(f" ❌ Erro @{p['username']}: {res.text}")

if __name__ == "__main__":
    sync_to_supabase()
