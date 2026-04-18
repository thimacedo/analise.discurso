import pandas as pd
import time
from coletor_apify import ColetorApify
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador_bertimbau import ClassificadorBERTimbau

def executar():
    print("="*60)
    print("🔬 FORENSENET - PIPELINE PERICIAL (METODOLOGIA VICHI)")
    print("="*60)
    
    # 1. Coleta
    print("\n[1/4] Iniciando Coleta Balanceada via Apify...")
    coletor = ColetorApify()
    df_bruto = coletor.pipeline_teste_balanceado(limite=10, posts_por_perfil=2, comentarios_por_post=10)
    
    if df_bruto is None or df_bruto.empty:
        print("❌ Falha na coleta ou nenhum dado encontrado. Abortando.")
        return
    
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
    
    # Salvar resultados em CSV
    arquivo_csv = proc.salvar_corpus(df_class, prefixo="corpus_classificado_final")
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
    perfil_hostilidade = miner.analise_perfil_odio(df_class)
    print("\n📊 Ranking de Hostilidade por Candidato:")
    print(perfil_hostilidade[['total_ataques']].head(10))
    
    print("\n" + "="*60)
    print("✅ ANÁLISE PERICIAL CONCLUÍDA COM SUCESSO")
    print("="*60)

if __name__ == "__main__":
    executar()
