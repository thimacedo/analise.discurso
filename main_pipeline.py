from instagram_collector import ForensicCollector
from corpus_builder import CorpusBuilder
from local_qwen_classifier import QwenLocalClassifier
from data_mining import DataMiner
from visualizer import DataVisualizer
from database.repository import DatabaseRepository
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Configuração de Candidatos
CANDIDATES = [
    "candidato_a_oficial",
    "candidato_b_oficial",
    "candidato_c_oficial"
]

def run_full_analysis():
    """
    Executa o pipeline completo de Análise Forense com IA LOCAL (Qwen 2.5 Coder).
    """
    print("="*60)
    print("🔬 FORENSENET - MONITORAMENTO DE DISCURSO POLÍTICO (v2.1 LOCAL IA)")
    print("="*60)
    
    # Inicializa Repositório de Dados
    db = DatabaseRepository()
    db.criar_tabelas()
    execucao = db.iniciar_execucao()
    
    # 1. Coleta baseada na conta @monitoramento.discurso
    print("\n[1/5] Iniciando coleta com @monitoramento.discurso...")
    try:
        collector = ForensicCollector()
        raw_df = collector.monitor_multiple_candidates(CANDIDATES, posts_per_candidate=15)
        
        if raw_df.empty:
            print("❌ Falha crítica: Nenhum dado coletado. Abortando pipeline.")
            db.finalizar_execucao(execucao.id, "FALHA", 0, 0, "Nenhum dado coletado")
            return
            
        print(f"📊 Total de comentários brutos: {len(raw_df)}")
        
        # Persistência de Candidatos e Comentários no DB
        print("💾 Persistindo dados brutos no Banco de Dados...")
        for _, row in raw_df.iterrows():
            candidato = db.salvar_candidato(row['candidate'], {})
            db.salvar_comentario(candidato.id, {
                'id_externo': str(row.get('id', row.get('id_externo'))),
                'post_id': str(row.get('post_id')),
                'autor_username': row.get('owner_username', row.get('autor_username')),
                'texto_bruto': row.get('text', row.get('texto_bruto')),
                'data_publicacao': pd.to_datetime(row.get('timestamp', row.get('data_publicacao')))
            })
            
    except Exception as e:
        print(f"❌ Erro na fase de coleta: {e}")
        db.finalizar_execucao(execucao.id, "ERRO_COLETA", 0, 0, str(e))
        return
    
    # 2. Construção de Corpus Linguístico
    print("\n[2/5] Construindo corpus e limpando metadados...")
    builder = CorpusBuilder()
    processed_df, freq_dist = builder.build_corpus(raw_df, text_column='text')
    builder.save_corpus_stats(processed_df)
    
    # 3. Classificação com IA LOCAL (Qwen via Ollama)
    print("\n[3/5] Classificando discurso de ódio (Qwen 2.5 Coder Local)...")
    classifier = QwenLocalClassifier()
    classified_df = classifier.classify_batch(processed_df['clean_text'].tolist())
    
    # Merge dos resultados (Classificação + Metadados Processados)
    # Alinhamos os índices para garantir o merge correto
    final_df = pd.concat([processed_df.reset_index(drop=True), classified_df.reset_index(drop=True)], axis=1)
    
    print("💾 Salvando classificações no Banco de Dados...")
    total_salvo = 0
    for _, row in final_df.iterrows():
        session = db.get_session()
        try:
            from database.models import Comentario
            # Busca pelo id_externo (que veio da coleta original no processed_df)
            id_ext = str(row.get('id', row.get('id_externo')))
            comentario = session.query(Comentario).filter(Comentario.id_externo == id_ext).first()
            
            if comentario:
                db.salvar_classificacao(comentario.id, {
                    'categoria_odio': row.get('category', 'NEUTRO'),
                    'score': float(row.get('score', 0.0)),
                    'confianca': float(row.get('confidence', 0.0)),
                    'modelo_versao': 'qwen2.5-coder-7b-local'
                })
                total_salvo += 1
        except Exception as e:
            print(f"⚠️ Erro ao salvar classificação: {e}")
        finally:
            session.close()

    # Mantém compatibilidade temporária com CSV
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
    viz.create_wordcloud(save_path='nuvem_geral.png')
    viz.plot_category_distribution()
    viz.plot_top_terms(n=25)
    
    if temporal_data is not None and not temporal_data.empty:
        viz.plot_hate_timeline(temporal_data, peaks)
        
    viz.generate_report()
    
    # Finaliza Log de Execução
    db.finalizar_execucao(execucao.id, "SUCESSO", len(raw_df), total_salvo)
    
    # 6. Sincronização Cloud (Opcional)
    print("\n[6/5] Sincronizando resultados com a nuvem...")
    try:
        from cloud_utils import upload_results_to_s3
        files_to_upload = [
            'corpus_classificado.csv',
            'relatorio_pericial.html',
            'nuvem_geral.png',
            'categories.png',
            'top_terms.png'
        ]
        upload_results_to_s3(files_to_upload)
    except Exception as e:
        print(f"⚠️ Alerta: Falha no upload cloud: {e}")
    
    print("\n" + "="*60)
    print("✅ ANÁLISE CONCLUÍDA COM SUCESSO")
    print(f"  -> {total_salvo} Comentários analisados localmente por Qwen")
    print("  -> Banco de Dados: odio_politica.db")
    print("="*60)
    
    return final_df

if __name__ == "__main__":
    run_full_analysis()

if __name__ == "__main__":
    run_full_analysis()

if __name__ == "__main__":
    run_full_analysis()