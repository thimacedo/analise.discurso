from instagram_collector import ForensicCollector
from corpus_builder import CorpusBuilder
from hate_classifier import HateSpeechClassifier
from data_mining import DataMiner
from visualizer import DataVisualizer
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração de Candidatos (Pode ser movido para um arquivo JSON ou DB no futuro)
CANDIDATES = [
    "candidato_a_oficial",
    "candidato_b_oficial",
    "candidato_c_oficial"
]

def run_full_analysis():
    """
    Executa o pipeline completo de Análise Forense seguindo a metodologia
    do Prof. Leonardo Vichi.
    """
    print("="*60)
    print("🔬 FORENSENET - MONITORAMENTO DE DISCURSO POLÍTICO")
    print("="*60)
    
    # 1. Coleta baseada na conta @monitoramento.discurso
    print("\n[1/5] Iniciando coleta com @monitoramento.discurso...")
    try:
        collector = ForensicCollector()
        raw_df = collector.monitor_multiple_candidates(CANDIDATES, posts_per_candidate=15)
        
        if raw_df.empty:
            print("❌ Falha crítica: Nenhum dado coletado. Abortando pipeline.")
            return
            
        print(f"📊 Total de comentários brutos: {len(raw_df)}")
    except Exception as e:
        print(f"❌ Erro na fase de coleta: {e}")
        return
    
    # 2. Construção de Corpus Linguístico
    print("\n[2/5] Construindo corpus e limpando metadados...")
    builder = CorpusBuilder()
    processed_df, freq_dist = builder.build_corpus(raw_df, text_column='text')
    builder.save_corpus_stats(processed_df)
    
    # 3. Classificação com Inteligência Híbrida
    print("\n[3/5] Classificando discurso de ódio (Metodologia Forense)...")
    classifier = HateSpeechClassifier()
    classified_results = classifier.classify_batch(processed_df['clean_text'].tolist())
    
    # Merge dos resultados
    final_df = pd.concat([processed_df, classified_results], axis=1)
    final_df.to_csv('corpus_classificado.csv', index=False, encoding='utf-8')
    
    # 4. Mineração de Dados e Análise de Redes
    print("\n[4/5] Minerando padrões e tendências temporais...")
    miner = DataMiner(final_df)
    temporal_data, peaks = miner.temporal_analysis()
    user_stats = miner.user_behavior_analysis()
    clustered_df, topics = miner.thematic_clustering()
    
    # 5. Visualização e Relatório Pericial
    print("\n[5/5] Gerando visualizações cinematográficas e relatório...")
    viz = DataVisualizer(final_df, freq_dist)
    
    # Exportação de ativos visuais
    viz.create_wordcloud(save_path='nuvem_geral.png')
    viz.plot_category_distribution()
    viz.plot_top_terms(n=25)
    
    if temporal_data is not None and not temporal_data.empty:
        viz.plot_hate_timeline(temporal_data, peaks)
        
    # Geração do output final (HTML)
    viz.generate_report()
    
    # 6. Upload para Cloud (Opcional - para Dashboard Vercel)
    print("\n[6/5] Sincronizando resultados com a nuvem...")
    from cloud_utils import upload_results_to_s3
    files_to_upload = [
        'corpus_classificado.csv',
        'relatorio_pericial.html',
        'nuvem_geral.png',
        'categories.png',
        'top_terms.png'
    ]
    upload_results_to_s3(files_to_upload)
    
    print("\n" + "="*60)
    print("✅ ANÁLISE CONCLUÍDA COM SUCESSO")
    print("  -> Relatório: relatorio_pericial.html")
    print("  -> Dados: corpus_classificado.csv")
    print("="*60)
    
    return final_df

if __name__ == "__main__":
    run_full_analysis()