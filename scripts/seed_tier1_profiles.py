"""
PASA v21 - Seed Tier 1: Injeta os 55 perfis de alto escalão (Blank State) na fila_coleta.
Força o motor autônomo a trabalhar nos peixes grandes imediatamente.
"""
import sys
import os

# Adiciona a raiz do projeto ao sys.path para permitir importações do 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_service import get_supabase_client

# Os 55 perfis prioritários (Governadores e Presidenciáveis)
TIER_1_PROFILES = [
    # Presidenciáveis 2022/2026
    "lulaoficial", "jairmessiasbolsonaro", "cirogomes", "simonetebetbr", 
    "fdaddio", "sorayathronicke", "felipe.davis.official", "pablocarvalhosp",
    # Governadores (Principais estados)
    "tarcisiogdf", "fernandohaddadoficial", "ratinho_junior", "rachelcadina",
    "romerojuca", "eduardoleite_", "onixlorenzoni", "waldirmaranhao",
    "maromendonca", "cacaleito", "renancalheiros", "paulodinizoficial",
    "ialvrocha", "zelucasoficial", "governadorcarlosmoises", "belivaldachagas",
    "jerimumlima", "gladsoncameli", "coronelmendonca_ac", "juniorsantista",
    "maurocarloslopes", "capitaoclaudio", "joaoazevedo_", "radepe",
    "evandroviegas", "fatonimaia", "casagoldenf", "helderbarbalho",
    "waldezgoes", "rinaldocamara", "paulofoletto", "renanfilho_oficial",
    "jerivasconcelos", "governadorbeltrame", "leilatavaresoficial",
    "carlosmendonca", "danielalimaoficial", "marcosmatooses", "valdircolatto",
    "betsymarques", "jorginhomello", "governodealagoas", "raulliramgovernador",
    "andrepimentaof", "sergiolelo", "carlinhosdealcantara", "geraldojuliooficial"
]

def inject_tier1():
    inserted_count = 0
    supabase = get_supabase_client()
    
    for username in TIER_1_PROFILES:
        # Upsert para evitar duplicidade se rodar mais de uma vez
        try:
            # Corrigido para o schema real: candidato_id e status=PENDENTE
            response = supabase.table('fila_coleta').upsert({
                'candidato_id': username,
                'status': 'PENDENTE',
                'prioridade': 1  # 1 = Alta prioridade
            }, on_conflict='candidato_id').execute()
            
            if response.data:
                inserted_count += 1
        except Exception as e:
            # Se falhar o upsert por falta de constraint, tenta insert simples
            try:
                response = supabase.table('fila_coleta').insert({
                    'candidato_id': username,
                    'status': 'PENDENTE',
                    'prioridade': 1
                }).execute()
                if response.data:
                    inserted_count += 1
            except Exception as e2:
                print(f"Erro ao injetar {username}: {e2}")
            
    print(f"[Seed Tier 1] {inserted_count} perfis de alto escalão injetados na fila. O motor autônomo já está moendo.")

if __name__ == "__main__":
    inject_tier1()
