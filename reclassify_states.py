import os
import httpx
import json

# Carregar config do .env manualmente para evitar dependências extras se possível
env_path = r"E:\projetos\sentinela-democratica\.env"
config = {}
with open(env_path, "r") as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            config[k.strip()] = v.strip().strip('"').strip("'")

url = config.get("SUPABASE_URL")
key = config.get("SUPABASE_KEY")

headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}

def get_candidates():
    r = httpx.get(f"{url}/rest/v1/candidatos?select=*", headers=headers)
    return r.json()

def update_candidate(id, data):
    r = httpx.patch(f"{url}/rest/v1/candidatos?id=eq.{id}", headers=headers, json=data)
    return r.status_code

def reclassify():
    candidates = get_candidates()
    print(f"Processando {len(candidates)} candidatos...")
    
    counts = {"BR": 0, "RN": 0, "SP": 0, "RJ": 0, "Outros": 0}
    
    for c in candidates:
        u = (c.get("username") or "").lower()
        n = (c.get("nome_completo") or "").lower()
        cargo = (c.get("cargo") or "").lower()
        
        novo_estado = c.get("estado") # Default atual
        
        # --- LÓGICA DE RECLASSIFICAÇÃO CRITERIOSA ---
        
        # PRIORIDADE 1: BR (Nacional)
        if any(x in u for x in ["lulaoficial", "jairmessiasbolsonaro", "michellebolsonaro", "geraldoalckmin", "simonetebet", "marinasilva", "flaviodino", "janjalula", "dilmarousseff", "zedirceu"]):
            novo_estado = "BR"
        elif "presidente" in cargo or "ministro" in cargo:
            novo_estado = "BR"
            
        # PRIORIDADE 2: RN (Base do Thiago / Foco Regional)
        elif any(x in u for x in ["rn", "natal", "parnamirim", "mossoro", "caico"]) or \
             any(x in n for x in ["rn", "natal", "parnamirim", "mossoro", "caico"]):
            novo_estado = "RN"
        elif any(x in u for x in ["fatimabezerra", "styvenson", "rogeriomarinho", "nataliabonavides", "allysonbezerra", "alvarodias", "isoldadantas", "mineiroptrn", "walteralves", "drazenaide"]):
            novo_estado = "RN"
        elif "vereador" in cargo and ("parnamirim" in n or "natal" in n or "rn" in n):
            novo_estado = "RN"
            
        # PRIORIDADE 3: SP
        elif any(x in u for x in ["tarcisiogdf", "boulos", "tabata", "pavanato", "holiday", "mbl", "mamaefalei", "kimkataguiri", "suplicy", "joaocampos"]): # joaocampos é PE, vamos corrigir abaixo
            novo_estado = "SP"
        elif "tarcisio" in n: novo_estado = "SP"

        # Correções de exceção
        if "joaocampos" in u: novo_estado = "PE"
        if "freixo" in u or "anielle" in u or "ramagem" in u or "glauber" in u or "lindbergh" in u: novo_estado = "RJ"
        if "moro" in u or "deltan" in u: novo_estado = "PR"
        if "caiado" in u: novo_estado = "GO"
        if "contarato" in u: novo_estado = "ES"
        if "janones" in u: novo_estado = "MG"
        if "nikolasferreira" in u: novo_estado = "MG"
        
        # Limpeza do "DF" genérico (se ainda for DF mas o nome/username sugerir outra coisa ou for deputado/senador)
        if novo_estado == "DF" and "senador" in cargo:
            # Tentar inferir estado pela lista de nomes se necessário, mas para 99 erros, mover para BR se for nacional
            if any(x in cargo for x in ["federal", "senador"]):
                # Se não sabemos o estado, BR é mais honesto que DF para quem atua em Brasília mas não é do DF
                novo_estado = "BR"

        if novo_estado != c.get("estado"):
            print(f"Atualizando @{u}: {c.get('estado')} -> {novo_estado}")
            update_candidate(c['id'], {"estado": novo_estado})
            if novo_estado in counts: counts[novo_estado] += 1
            else: counts["Outros"] += 1

    print("\nReclassificação concluída!")
    print(json.dumps(counts, indent=2))

if __name__ == "__main__":
    reclassify()
