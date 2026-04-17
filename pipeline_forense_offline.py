import pandas as pd
import time
import os
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador_bertimbau import ClassificadorBERTimbau

def executar_offline():
    print("="*60)
    print("🔬 FORENSENET - PIPELINE PERICIAL (MODO OFFLINE)")
    print("="*60)
    
    # 1. Carregamento Local
    print("\n[1/4] Carregando Base de Dados Local...")
    arquivo_local = "dados_brutos_20260412_181602.csv"
    if not os.path.exists(arquivo_local):
        print(f"❌ Arquivo {arquivo_local} não encontrado.")
        return
        
    df_bruto = pd.read_csv(arquivo_local)
    # Ajustando colunas para o padrão do nosso pipeline se necessário
    if 'texto' not in df_bruto.columns and 'text' in df_bruto.columns:
        df_bruto.rename(columns={'text': 'texto'}, inplace=True)
    if 'candidato' not in df_bruto.columns and 'username' in df_bruto.columns:
        df_bruto.rename(columns={'username': 'candidato'}, inplace=True)
        
    print(f"✅ {len(df_bruto)} comentários carregados.")
    
    # Pegar apenas uma amostra para processar rápido no teste
    df_bruto = df_bruto.head(100)
    
    # 2. Processamento
    print("\n[2/4] Iniciando Pré-processamento Forense...")
    proc = ProcessadorCorpus()
    df_proc = proc.processar_dataframe(df_bruto, coluna_texto='texto')
    
    if df_proc.empty:
        print("❌ Nenhum texto restou após o processamento. Abortando.")
        return

    # 3. Classificação
    print("\n[3/4] Iniciando Classificação com BERTimbau...")
    clas = ClassificadorBERTimbau()
    df_class = clas.processar_corpus_completo(df_proc, coluna_texto='texto_limpo')
    
    # Salvar resultados
    arquivo_csv = proc.salvar_corpus(df_class, prefixo="corpus_classificado_teste_offline")
    print(f"✅ Dados salvos em: {arquivo_csv}")
    
    # 4. Mineração e Visualização
    print("\n[4/4] Minerando Padrões e Gerando Visualizações...")
    miner = MineradorCorpus()
    
    # N-gramas
    ngrams = miner.extrair_ngrams_periciais(df_class, n=2, top_k=10)
    print("\n🔥 Top 10 Bigramas de Ofensa/Política:")
    for ng, freq in ngrams:
        print(f" - '{ng}': {freq} ocorrências")
    
    # Nuvens de palavras
    print("\n☁️ Gerando Nuvens de Palavras...")
    miner.gerar_nuvem_pericial(df_class, prefixo="nuvem_forense")
    
    categorias_presentes = df_class['categoria_odio'].unique()
    for cat in categorias_presentes:
        if cat != 'neutro':
            miner.gerar_nuvem_pericial(df_class, categoria_odio=cat, prefixo="nuvem_forense")
            
    # Perfil de hostilidade
    if 'candidato' in df_class.columns:
        perfil_hostilidade = miner.analise_perfil_odio(df_class)
        print("\n📊 Ranking de Hostilidade por Candidato:")
        print(perfil_hostilidade[['total_ataques']].head(10))
    
    print("\n" + "="*60)
    print("✅ ANÁLISE PERICIAL CONCLUÍDA COM SUCESSO (OFFLINE)")
    print("="*60)

if __name__ == "__main__":
    executar_offline()
