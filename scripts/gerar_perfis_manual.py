import json
from datetime import datetime

entradas_brutas = [
    "https://www.instagram.com/flaviobolsonaro/",
    "https://www.instagram.com/hilton_erika/",
    "https://www.instagram.com/lindberghfarias/",
    "https://www.instagram.com/jairmessiasbolsonaro/",
    "https://www.instagram.com/nikolasferreiradm/",
    "https://www.instagram.com/dep.eduardobolsonaro/",
    "https://www.instagram.com/guilhermeboulos.oficial/",
    "vereadoriraniguedes",
    "michaelborgesrn",
    "vereadorederqueiroz",
    "rodrigocruz_rn",
    "drjonasgodeiro",
    "binhodeambrosio",
    "cctv.parnamirim",
    "professordiegoamerico",
    "vereadoreuricodajapao",
    "marleidecunharn",
    "vereadorarhalessarn",
    "thiagofernandesrn",
    "https://www.instagram.com/lulaoficial"
]

def limpar_username(entrada):
    """Remove URLs e barras, deixando apenas o username limpo"""
    user = entrada.replace("https://www.instagram.com/", "").replace("http://www.instagram.com/", "")
    user = user.strip().strip("/")
    return user

# Limpa e remove duplicatas
perfis_limpos = list(dict.fromkeys([limpar_username(e) for e in entradas_brutas if limpar_username(e)]))

dados = {
    "ultima_atualizacao": datetime.now().isoformat(),
    "perfis": perfis_limpos
}

arquivo_saida = "perfis_monitorados.json"
with open(arquivo_saida, "w", encoding="utf-8") as f:
    json.dump(dados, f, ensure_ascii=False, indent=2)

print(f"Sucesso: Arquivo '{arquivo_saida}' criado com {len(perfis_limpos)} perfis.")
