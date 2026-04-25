import os
import httpx
import json

env_path = r"E:\projetos\sentinela-democratica\.env"
config = {}
with open(env_path, "r") as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            config[k.strip()] = v.strip().strip('"').strip("'")

url = config.get("SUPABASE_URL")
key = config.get("SUPABASE_KEY")
headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}

def get_candidates():
    r = httpx.get(f"{url}/rest/v1/candidatos?select=*", headers=headers)
    return r.json()

def update_candidate(id, data):
    r = httpx.patch(f"{url}/rest/v1/candidatos?id=eq.{id}", headers=headers, json=data)
    return r.status_code

# LISTAS DE EXCLUSIVIDADE
PRESIDENCIAVEIS = ["lulaoficial", "jairmessiasbolsonaro", "michellebolsonaro", "geraldoalckmin_", "simonetebet", "marinasilvaoficial", "flaviodino", "janjalula", "dilmarousseff", "zedirceuoficial"]
RN_BASE = ["fatimabezerra13", "senadorstyvensonvalentim", "rogeriomarinho", "nataliabonavides", "allysonbezerra.rn", "alvarodiasrn", "isoldadantaspt", "mineiroptrn", "walteralvesrn", "drazenaide", "capitaostyvensonsenador"]

def reclassify_strict():
    candidates = get_candidates()
    print(f"Iniciando Reclassificação Rigorosa ({len(candidates)} alvos)...")
    
    for c in candidates:
        u = (c.get("username") or "").lower()
        n = (c.get("nome_completo") or "").lower()
        cargo = (c.get("cargo") or "").lower()
        estado_atual = c.get("estado")
        
        # DEFINIÇÃO DO NOVO ESTADO (Default: Manter o que tem, a menos que mude pelas regras)
        novo_estado = estado_atual

        # REGRA 1: BR (Apenas Elite Presidencial)
        if u in PRESIDENCIAVEIS or "presidente" in cargo:
            novo_estado = "BR"
        
        # REGRA 2: RN (Foco Regional Específico)
        elif u in RN_BASE or any(x in u for x in ["rn", "natal", "parnamirim", "mossoro"]):
            novo_estado = "RN"
            
        # REGRA 3: RJ
        elif any(x in u for x in ["freixo", "anielle", "ramagem", "glauber", "lindbergh"]):
            novo_estado = "RJ"

        # REGRA 4: SP
        elif any(x in u for x in ["tarcisiogdf", "boulos", "tabata", "pavanato", "holiday", "suplicy"]):
            novo_estado = "SP"

        # REGRA 5: MG
        elif any(x in u for x in ["janones", "nikolasferreira"]):
            novo_estado = "MG"

        # REGRA 6: LIMPEZA DO DF (Federal sem base local no DF vai para BR ou Estado Original)
        if novo_estado == "DF":
            if any(x in cargo for x in ["federal", "senador", "ministro"]):
                # Se é do congresso e não é elite presidencial, tentamos manter o estado de origem se soubermos,
                # mas como a ordem do usuário é tirar do DF, se não cair nas regras acima, vai para BR (Atuação Nacional).
                novo_estado = "BR"

        if novo_estado != estado_atual:
            print(f"FIX: @{u} [{estado_atual} -> {novo_estado}]")
            update_candidate(c['id'], {"estado": novo_estado})

    print("\nLimpeza de duplicidade e reposicionamento concluída!")

if __name__ == "__main__":
    reclassify_strict()
