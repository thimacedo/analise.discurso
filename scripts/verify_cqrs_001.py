import pandas as pd
from processing.text_processor import TextProcessor
import os

def verify():
    print("[INFO] Iniciando Verificacao de Blindagem de Seguranca (CQRS-001)...")
    
    # Criar pasta de logs se não existir
    if not os.path.exists('logs'):
        os.makedirs('logs')

    tp = TextProcessor()
    
    # Dados de teste com lixo sensível
    data = {
        'text': [
            "O candidato X é um lixo! CPF 123.456.789-00",
            "Ligue para 11 98765-4321 para saber a verdade.",
            "Minha chave mestre é abcdef1234567890abcdef1234567890",
            "Texto limpo sem nada demais."
        ]
    }
    
    df = pd.DataFrame(data)
    df_proc = tp.processar_dataframe(df)
    
    print("\n--- RESULTADOS DA BLINDAGEM ---")
    for i, row in df_proc.iterrows():
        print(f"Original: {data['text'][i]}")
        print(f"Processado: {row['texto_limpo']}")
        print("-" * 30)
    
    # Verificação lógica
    success = True
    if "123.456.789-00" in df_proc.iloc[0]['texto_limpo']:
        print("[FAIL] CPF não foi redigido!")
        success = False
    if "98765-4321" in df_proc.iloc[1]['texto_limpo']:
        print("[FAIL] Telefone não foi redigido!")
        success = False
    if "abcdef1234567890" in df_proc.iloc[2]['texto_limpo']:
        print("[FAIL] API Key não foi redigida!")
        success = False

    if success:
        print("\n[OK] TUDO LIMPO, MORTY! A seguranca esta impenetravel! *belch*")
    else:
        print("\n[ERROR] TEMOS UM VAZAMENTO! VOLTANDO AO LABORATORIO!")

if __name__ == "__main__":
    verify()
