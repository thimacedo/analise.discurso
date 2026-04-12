# orquestrador.py
import sys
import os
import traceback
from datetime import datetime
from coletor_seguidos import ColetorSeguro
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador import ClassificadorOdio
from cloud_utils import upload_para_s3

def log(etapa, status, mensagem=""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {etapa:20} - {status:8} - {mensagem}")

def executar_etapa(nome, funcao, *args, **kwargs):
    log(nome, "INICIADO")
    try:
        resultado = funcao(*args, **kwargs)
        log(nome, "SUCESSO")
        return resultado
    except Exception as e:
        log(nome, "FALHA", str(e))
        traceback.print_exc()
        sys.exit(1)

# -------------------- ETAPAS UNIFICADAS --------------------

def etapa_coleta(posts_por_perfil=3):
    coletor = ColetorSeguro()
    df, _ = coletor.coletar_todos_seguidos(posts_por_perfil=posts_por_perfil)
    if df.empty:
        raise Exception("Nenhum dado coletado dos perfis seguidos.")
    return df

def main():
    print("🚀 INICIANDO MONITORAMENTO FORENSE (Seguidores)\n")

    # 1. Coleta Dinâmica
    df_bruto = executar_etapa("COLETA", etapa_coleta, posts_por_perfil=3)

    # 2. Pré-processamento
    proc = ProcessadorCorpus()
    df_proc, freq = executar_etapa("PROCESSAMENTO", proc.processar_dataframe, df_bruto)
    proc.gerar_nuvem_palavras(freq, salvar=True)

    # 3. Mineração e Classificação
    miner = MineradorCorpus()
    miner.analisar_frequencia_ngrams(df_proc)
    
    clas = ClassificadorOdio()
    df_final = executar_etapa("CLASSIFICAÇÃO", clas.classificar_dataframe, df_proc)

    # 4. Sincronização Cloud
    temp_file = "corpus_classificado_latest.csv"
    df_final.to_csv(temp_file, index=False, encoding='utf-8-sig')
    
    executar_etapa("CLOUD SYNC", upload_para_s3, temp_file, "corpus_classificado_latest.csv")

    print("\n✅ PIPELINE CONCLUÍDO E SINCRONIZADO!")

if __name__ == "__main__":
    main()
