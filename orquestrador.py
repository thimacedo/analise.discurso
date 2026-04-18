import sys
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

from coletor import ColetorPublico
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador import ClassificadorOdio
from visualizer import DataVisualizer
from candidato_analisador import AnalisadorPerfis
from database.repository import DatabaseRepository
from memoria import MemoriaExecucao

# Importação opcional do cloud_utils
try:
    from cloud_utils import upload_para_s3
except ImportError:
    upload_para_s3 = None

def log(etapa, status, msg=""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {etapa:20} | {status:8} | {msg}")

def main():
    # Registrar esta execução
    memoria = MemoriaExecucao()
    memoria.registrar_execucao()
    
    # Inicializa banco de dados
    db = DatabaseRepository()
    db.criar_tabelas()
    execucao_db = db.iniciar_execucao()

    limite_perfis = int(os.getenv('COLETA_LIMITE_PERFIS', 5))
    posts_por_perfil = int(os.getenv('COLETA_POSTS_POR_PERFIL', 2))

    print(f"--- INICIANDO PIPELINE ANALISE DISCURSO ---")
    
    # 1. COLETA SEGURA (VIA INSTAGRAPI)
    coletor = ColetorPublico()
    df_bruto = coletor.coletar_todos(posts_por_perfil=posts_por_perfil)
    if df_bruto.empty:
        log("COLETA", "FALHA", "Sem dados coletados. Rode 'python atualizar_perfis.py' primeiro?")
        db.finalizar_execucao(execucao_db.id, 'FALHA_COLETA', 0, 0)
        return

    # 2. ENRIQUECIMENTO DE PERFIS (IA Gratuita)
    log("ENRIQUECIMENTO", "INICIO", "Analisando perfis dos candidatos com IA...")
    analisador = AnalisadorPerfis()
    perfis_unicos = df_bruto['candidato'].unique().tolist()
    
    metadados_perfis = {}
    for perfil in perfis_unicos:
        bio_data = analisador.obter_bio_perfil(perfil)
        info_candidato = analisador.analisar_perfil(
            username=perfil, 
            bio=bio_data.get('bio', ''), 
            nome_completo=bio_data.get('nome_completo', '')
        )
        metadados_perfis[perfil] = info_candidato

    # Salva candidatos no banco de dados
    candidatos_db = {}
    for perfil, dados in metadados_perfis.items():
        candidato = db.salvar_candidato(perfil, dados)
        candidatos_db[perfil] = candidato.id

    # Adiciona as colunas de metadata ao DataFrame bruto
    for coluna in ['cargo', 'sexo', 'raca', 'estado', 'partido', 'ideologia']:
        df_bruto[coluna] = df_bruto['candidato'].map(lambda x: metadados_perfis.get(x, {}).get(coluna, 'N/A'))

    # 3. PROCESSAMENTO
    proc = ProcessadorCorpus()
    df_proc, freq = proc.processar_dataframe(df_bruto, coluna_texto='texto')
    proc.gerar_estatisticas(df_proc)

    # 4. CLASSIFICAÇÃO
    clas = ClassificadorOdio()
    df_final = clas.classificar_dataframe(df_proc)
    df_final['is_hate_speech'] = df_final['categoria_odio'] != 'neutro'
    df_final['primary_category'] = df_final['categoria_odio']

    # 5. MINERAÇÃO
    miner = MineradorCorpus()
    ngrams_freq = miner.analisar_frequencia_ngrams(df_final)
    daily_hate, peaks = miner.analise_temporal(df_final)

    # 6. VISUALIZAÇÃO
    viz = DataVisualizer(df_final, freq)
    viz.create_wordcloud(save_path='nuvem_geral.png')
    viz.plot_category_distribution(save_path='categories.png')
    viz.plot_top_terms(n=25, save_path='top_terms.png')
    if not daily_hate.empty:
        viz.plot_hate_timeline(daily_hate, peaks, save_path='timeline.png')
    viz.generate_report(output_path='relatorio_pericial.html')

    # 7. EXPORTAÇÃO CSV
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    df_final.to_csv(f"resultado_{ts}.csv", index=False, encoding='utf-8-sig')
    os.makedirs("api", exist_ok=True)
    dashboard_file = os.path.join("api", "dados_latest.csv")
    df_final.to_csv(dashboard_file, index=False, encoding='utf-8-sig')
    
    if os.getenv('AWS_BUCKET_NAME') and upload_para_s3:
        upload_para_s3(dashboard_file, "dados_latest.csv")

    # 8. SALVA NO BANCO DE DADOS
    log("BANCO_DADOS", "INICIO", "Salvando resultados no banco local...")
    total_salvo = 0
    
    for _, row in df_final.iterrows():
        candidato_id = candidatos_db.get(row['candidato'])
        if not candidato_id:
            continue
        
        # Gera um ID único se o scraper não trouxer um
        id_externo = str(row.get('id_comentario')) if row.get('id_comentario') else str(hash(row.get('texto', '') + row.get('autor', '')))
        post_id = str(row.get('id_post')) if row.get('id_post') else 'unknown'
            
        comentario = db.salvar_comentario(candidato_id, {
            'id_externo': id_externo,
            'post_id': post_id,
            'autor_username': row.get('autor', 'anon'),
            'texto_bruto': row.get('texto', ''),
            'texto_limpo': row.get('texto_limpo', ''),
            'data_publicacao': row.get('data', None),
            'likes': row.get('likes', 0)
        })
        
        if comentario:
            db.salvar_classificacao(comentario.id, {
                'categoria_odio': row.get('categoria_odio', 'neutro'),
                'score': row.get('severidade', 0) / 10.0, # Converte 0-10 para 0-1
                'confianca': 0.75 if row.get('categoria_odio') != 'neutro' else 0.99,
                'modelo_versao': 'hybrid_v1'
            })
            total_salvo += 1
    
    db.finalizar_execucao(execucao_db.id, 'SUCESSO', len(df_bruto), total_salvo)
    log("BANCO_DADOS", "PRONTO", f"{total_salvo} comentários salvos no banco")

    log("ORQUESTRADOR", "PRONTO", "Pipeline executado com sucesso.")

if __name__ == "__main__":
    main()