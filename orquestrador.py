import sys
import os
import traceback
from datetime import datetime
from coletor_seguidos import ColetorSeguro
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador import ClassificadorOdio
from cloud_utils import upload_para_s3

def log(etapa, status, msg=""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {etapa:20} | {status:8} | {msg}")

def main():
    print("🚀 INICIANDO MONITORAMENTO FORENSE (Seguidores)\n")

    # 1. COLETA (Dinâmica via Seguidores)
    coletor = ColetorSeguro()
    df_bruto, _ = coletor.coletar_todos_seguidos(posts_por_perfil=3)
    
    if df_bruto.empty:
        log("COLETA", "FALHA", "Nenhum dado extraído.")
        return

    # 2. PROCESSAMENTO
    proc = ProcessadorCorpus()
    df_proc, freq = proc.processar_dataframe(df_bruto)
    proc.gerar_nuvem_palavras(freq, salvar=True)

    # 3. MINERAÇÃO & CLASSIFICAÇÃO
    miner = MineradorCorpus()
    miner.analisar_frequencia_ngrams(df_proc)
    
    clas = ClassificadorOdio()
    df_final = clas.classificar_dataframe(df_proc)

    # 4. EXPORTAÇÃO E NUVEM
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_csv = f"resultado_latest.csv"
    df_final.to_csv(local_csv, index=False, encoding='utf-8-sig')
    
    # Sincronização S3
    log("CLOUD", "SYNC", "Enviando dados para o S3...")
    upload_para_s3(local_csv, "corpus_classificado_latest.csv")
    
    print("\n✅ PIPELINE COMPLETO E SINCRONIZADO!")

if __name__ == "__main__":
    main()
