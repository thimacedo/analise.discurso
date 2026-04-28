import json
import os
from coletor import ColetorSeguro

def sincronizar():
    print("--- Iniciando Sincronizacao de Perfis ---")
    try:
        c = ColetorSeguro()
        perfis = c.obter_perfis_seguidos()
        
        if perfis:
            dados = {
                "perfis": perfis,
                "total": len(perfis)
            }
            with open("perfis_monitorados.json", "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)
            print(f"Sucesso: {len(perfis)} perfis smonitorados em 'perfis_monitorados.json'")
        else:
            print("Aviso: Nenhun perfil encontrado ou erro no login.")
            
    except Exception as e:
        print(f"Erro fatal na sincronizacao: {e}")

if __name__ == "__main__":
    sincronizar()
