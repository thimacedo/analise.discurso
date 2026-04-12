from instagram_collector import InstagramCollector
from corpus_builder import CorpusBuilder
from hate_classifier import HateSpeechClassifier
from data_mining import DataMiner
from visualizer import DataVisualizer
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def run_forensic_analysis(candidates, posts_per_candidate=20):
    """
    Pipeline completo seguindo metodologia do prof. Leonardo Vichi
    """
    print("="*60)
    print("🔬 FORENSENET - Análise de Discurso de Ódio")
    print("Metodologia: Linguística Forense + Tecnologia Digital")
    print("="*60)
    
    # 1. Coleta de dados
    print("\n[1/5] Coletando dados do Instagram...")
    collector = InstagramCollector(
        username=os.getenv('INSTAGRAM_USERNAME'),
        password=os.getenv('INSTAGRAM_PASSWORD')
    )
    
    all_comments = []
    for candidate in candidates:
        try:
            df = collector.collect_politician_posts(candidate, posts_per_candidate)
            all_comments.append(df)
            print(f"  ✓ Coletados {len(df)} comentários de @{candidate}")
        except Exception as e:
            print(f"  ✗ Erro ao coletar @{candidate}: {e}")
    
    if not all_comments:
        print("❌ Nenhum comentário coletado. Verifique as credenciais.")
        return
    
    raw_df = pd.concat(all_comments, ignore_index=True)
    raw_df.to_csv('dados_brutos.csv', index=False, encoding='utf-8')
    print(f"  ✓ Total de comentários coletados: {len(raw_df)}")
    
    # 2. Construção do corpus
    print("\n[2/5] Construindo corpus linguístico...")
    corpus_builder = CorpusBuilder()
    processed_df, freq_dist = corpus_builder.build_corpus(raw_df)
    corpus_builder.save_corpus_stats(processed_df)
    print(f"  ✓ Corpus construído: {len(processed_df)} documentos, {len(freq_dist)} termos únicos")
    
    # 3. Classificação de discurso de ódio
    print("\n[3/5] Classificando discurso de ódio...")
    classifier = HateSpeechClassifier()
    classified_results = classifier.classify_batch(processed_df['clean_text'].tolist())
    classified_df = pd.concat([processed_df, classified_results], axis=1)
    classified_df.to_csv('corpus_classificado.csv', index=False, encoding='utf-8')
    
    hate_count = classified_df['is_hate_speech'].sum()
    print(f"  ✓ {hate_count} comentários classificados como discurso de ódio ({hate_count/len(classified_df)*100:.2f}%)")
    
    # 4. Mineração de dados
    print("\n[4/5] Realizando mineração de dados...")
    miner = DataMiner(classified_df)
    
    temporal_data, peaks = miner.temporal_analysis()
    user_stats = miner.user_behavior_analysis()
    clustered_df, cluster_topics = miner.thematic_clustering()
    co_occurrence_network = miner.co_occurrence_network()
    
    print(f"  ✓ Picos detectados: {len(peaks)} eventos")
    if len(user_stats) > 0:
        print(f"  ✓ Usuários com maior risco: {user_stats.head(3).index.tolist()}")
    
    # 5. Visualizações
    print("\n[5/5] Gerando visualizações...")
    visualizer = DataVisualizer(classified_df, freq_dist)
    
    # Nuvem de palavras geral
    visualizer.create_wordcloud(save_path='nuvem_geral.png')
    
    # Nuvens por categoria
    for category in ['racismo', 'homofobia', 'transfobia', 'misoginia', 'xenofobia']:
        if category in classified_df['primary_category'].values:
            visualizer.create_wordcloud(category=category, save_path=f'nuvem_{category}.png')
    
    # Gráficos
    if len(temporal_data) > 0:
        visualizer.plot_hate_timeline(temporal_data, peaks)
    visualizer.plot_category_distribution()
    visualizer.plot_top_terms(n=25)
    
    # Relatório final
    visualizer.generate_report()
    
    print("\n" + "="*60)
    print("✅ ANÁLISE CONCLUÍDA!")
    print("Arquivos gerados:")
    print("  - dados_brutos.csv")
    print("  - corpus_processado.csv")
    print("  - corpus_classificado.csv")
    print("  - frequencias_terminos.csv")
    print("  - relatorio_pericial.html")
    print("  - nuvem_*.png (vários formatos)")
    print("  - timeline.png, categories.png, top_terms.png")
    print("="*60)
    
    return classified_df

if __name__ == "__main__":
    # Configurar candidatos para monitoramento
    CANDIDATES = [
        "candidato_a_instagram",
        "candidato_b_instagram",
        "candidato_c_instagram"
    ]
    
    # Executar análise
    results = run_forensic_analysis(CANDIDATES, posts_per_candidate=20)