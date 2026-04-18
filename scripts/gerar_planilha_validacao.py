import json
import os
import pandas as pd

def gerar_planilha():
    perfis_file = "perfis_monitorados.json"
    output_file = "validacao_perfis.csv"
    
    if not os.path.exists(perfis_file):
        print("❌ Arquivo perfis_monitorados.json não encontrado.")
        return

    with open(perfis_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    df = pd.DataFrame(data.get("perfis_detalhes", []))
    
    # Reordenar colunas para facilitar a edição humana
    cols = ["username", "categoria", "subcategoria", "prioridade"]
    df = df[cols]
    
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"✅ Planilha de validação gerada: {output_file}")
    print("👉 Por favor, abra este arquivo, corrija as categorias (ex: Flavio Bolsonaro para 'nacional') e salve.")

if __name__ == "__main__":
    gerar_planilha()
