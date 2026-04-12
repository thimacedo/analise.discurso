import sys
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

from coletor import ColetorSeguro
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador import ClassificadorOdio
from visualizer import DataVisualizer
from candidato_analisador import AnalisadorPerfis

# CORREÇÃO #5: importação opcional do cloud_utils
try:
    from cloud_utils import upload_para_s3
except ImportError:
    upload_para_s3 = None

def log(etapa, status, msg=""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {etapa:20} | {status:8} | {msg}")

def main():
    IG_USERNAME = os.getenv('IG_USERNAME')
    IG_PASSWORD = os.getenv('IG_PASSWORD')
    if not IG_USERNAME or not IG_PASSWORD:
        print("❌ ERRO: IG_USERNAME e IG_PASSWORD não foram encontrados.")
        sys.exit(1)
    
    # Registrar esta execução
    from memoria import MemoriaExecucao
    memoria = MemoriaExecucao()
    memoria.registrar_execucao()

    limite_perfis = int(os.getenv('COLETA_LIMITE_PERFIS', 5))
    posts_por_perfil = int(os.getenv('COLETA_POSTS_POR_PERFIL', 2))

    print(f"🚀 INICIANDO PIPELINE ANÁLISE DISCURSO")
    
    # 1. COLETA
    coletor = ColetorSeguro()
    df_bruto = coletor.coletar_todos_seguidos(posts_por_perfil=posts_por_perfil, limite_perfis=limite_perfis)
    if df_bruto.empty:
        log("COLETA", "FALHA", "Sem dados coletados.")
        return

    # 2. ENRIQUECIMENTO DE PERFIS (IA Gratuita)
    log("ENRIQUECIMENTO", "INÍCIO", "Analisando perfis dos candidatos com IA...")
    analisador = AnalisadorPerfis()
    perfis_unicos = df_bruto['candidato'].unique().tolist()
    
    metadados_perfis = {}
    for perfil in perfis_unicos:
        bio_data = coletor.obter_bio_perfil(perfil)
        info_candidato = analisador.analisar_perfil(
            username=perfil, 
            bio=bio_data.get('bio', ''), 
            nome_completo=bio_data.get('nome_completo', '')
        )
        metadados_perfis[perfil] = info_candidato

    # Adiciona as colunas de metadata ao DataFrame bruto
    for coluna in ['cargo', 'sexo', 'raca', 'estado', 'partido', 'ideologia']:
        df_bruto[coluna] = df_bruto['candidato'].map(lambda x: metadados_perfis.get(x, {}).get(coluna, 'N/A'))

    # 3. PROCESSAMENTO
    proc = ProcessadorCorpus()
    df_proc, freq = proc.processar_dataframe(df_bruto, coluna_texto='texto')
    proc.gerar_estatisticas(df_proc)

    clas = ClassificadorOdio()
    df_final = clas.classificar_dataframe(df_proc)
    df_final['is_hate_speech'] = df_final['categoria_odio'] != 'neutro'
    df_final['primary_category'] = df_final['categoria_odio']

    miner = MineradorCorpus()
    ngrams_freq = miner.analisar_frequencia_ngrams(df_final)
    daily_hate, peaks = miner.analise_temporal(df_final)

    viz = DataVisualizer(df_final, freq)
    viz.create_wordcloud(save_path='nuvem_geral.png')
    viz.plot_category_distribution(save_path='categories.png')
    viz.plot_top_terms(n=25, save_path='top_terms.png')
    if not daily_hate.empty:
        viz.plot_hate_timeline(daily_hate, peaks, save_path='timeline.png')
    viz.generate_report(output_path='relatorio_pericial.html')

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    df_final.to_csv(f"resultado_{ts}.csv", index=False, encoding='utf-8-sig')
    os.makedirs("api", exist_ok=True)
    dashboard_file = os.path.join("api", "dados_latest.csv")
    df_final.to_csv(dashboard_file, index=False, encoding='utf-8-sig')
    # CORREÇÃO #5: só tenta upload se a função existir e a chave estiver configurada
    if os.getenv('AWS_BUCKET_NAME') and upload_para_s3:
        upload_para_s3(dashboard_file, "dados_latest.csv")

    log("ORQUESTRADOR", "PRONTO", "Pipeline executado com sucesso.")

if __name__ == "__main__":
    main()