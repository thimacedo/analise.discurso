import os
import sys
import requests
import argparse
from dotenv import load_dotenv

load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SENTINELA_SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def list_targets():
    url = f"{SUPABASE_URL}/rest/v1/candidatos?select=username,nome_completo,status_monitoramento&status_monitoramento=eq.Ativo"
    res = requests.get(url, headers=HEADERS)
    if res.status_code == 200:
        targets = res.json()
        print(f"\n📊 TOTAL DE ALVOS ATIVOS: {len(targets)}")
        print("-" * 50)
        for t in targets:
            print(f"  @{t['username']:<20} | {t['nome_completo']}")
    else:
        print(f"❌ Erro ao listar: {res.text}")

def add_target(username, nome, cargo, estado):
    username = username.strip().replace("@", "")
    data = {
        "username": username,
        "nome_completo": nome,
        "cargo": cargo,
        "estado": estado,
        "status_monitoramento": "Ativo"
    }
    url = f"{SUPABASE_URL}/rest/v1/candidatos"
    headers_upsert = HEADERS.copy()
    headers_upsert["Prefer"] = "resolution=merge-duplicates"
    
    res = requests.post(url, headers=headers_upsert, json=data)
    if res.status_code in [200, 201]:
        print(f"✅ Sucesso: @{username} adicionado/atualizado no monitoramento.")
    else:
        print(f"❌ Erro ao adicionar: {res.text}")

def remove_target(username):
    username = username.strip().replace("@", "")
    # Em vez de deletar, apenas desativamos o monitoramento
    data = {"status_monitoramento": "Inativo"}
    url = f"{SUPABASE_URL}/rest/v1/candidatos?username=eq.{username}"
    
    res = requests.patch(url, headers=HEADERS, json=data)
    if res.status_code in [200, 204]:
        print(f"✅ Sucesso: @{username} removido do monitoramento ativo.")
    else:
        print(f"❌ Erro ao remover: {res.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gestor de Alvos - Sentinela Democrática")
    parser.add_argument("action", choices=["list", "add", "remove"], help="Ação a ser executada")
    parser.add_argument("--username", help="Username do Instagram")
    parser.add_argument("--nome", help="Nome completo", default="Não informado")
    parser.add_argument("--cargo", help="Cargo político", default="Monitorado")
    parser.add_argument("--estado", help="UF", default="BR")

    args = parser.parse_args()

    if args.action == "list":
        list_targets()
    elif args.action == "add":
        if not args.username:
            print("❌ Erro: --username é obrigatório para adicionar.")
        else:
            add_target(args.username, args.nome, args.cargo, args.estado)
    elif args.action == "remove":
        if not args.username:
            print("❌ Erro: --username é obrigatório para remover.")
        else:
            remove_target(args.username)
