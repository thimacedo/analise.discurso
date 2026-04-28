import os
import json
import requests

# Este script usará uma técnica de "Self-Classification" - como sou uma IA, 
# posso processar a lista e categorizar.
# Vou ler o relatório de gaps e gerar a classificação final.

def classify_with_llm_logic():
    report_path = "data/gap_analysis_report.json"
    if not os.path.exists(report_path):
        print("❌ Relatório de gaps não encontrado.")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        profiles = json.load(f)

    print(f"🧠 Processando {len(profiles)} perfis para classificação de cenário...")

    # Como sou o Gemini, vou aplicar meu conhecimento sobre esses nomes públicos
    for p in profiles:
        u = p['username'].lower()
        n = p['full_name'].lower()
        
        # Lógica de Classificação Baseada em Conhecimento de Domínio (Brasil)
        if any(x in u or x in n for x in ["vereador", "parnamirim", "natal", "camara", "prefeito", "prefeita"]):
            p['scenario'] = "Municipal"
        elif any(x in u or x in n for x in ["deputado estadual", "governador", "fatima bezerra", "rn"]):
            # Se tiver 'rn' mas não for claramente municipal, é estadual (RN)
            if p.get('scenario') != "Municipal":
                p['scenario'] = "Estadual"
            else:
                p['scenario'] = "Municipal" # Parnamirim/Natal vencem RN
        elif any(x in u or x in n for x in ["senador", "lula", "bolsonaro", "ministro", "stf", "tse", "deputado federal", "geraldo alckmin", "janja", "dilma"]):
            p['scenario'] = "Nacional"
        else:
            # Casos ambíguos ou perfis de mídia/notícias
            if "noticias" in u or "blog" in u or "news" in u:
                p['scenario'] = "Mídia/Informativo"
            else:
                p['scenario'] = "Nacional" # Fallback

    output_path = "data/classified_profiles.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=4, ensure_ascii=False)
    
    # Mostrar estatísticas
    stats = {}
    for p in profiles:
        s = p['scenario']
        stats[s] = stats.get(s, 0) + 1
    
    print("\n📊 Estatísticas de Classificação:")
    for s, count in stats.items():
        print(f"  - {s}: {count}")
    
    print(f"\n✅ Arquivo smonitorado em {output_path}")

if __name__ == "__main__":
    classify_with_llm_logic()
