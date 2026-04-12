import sys
import os
import traceback
from datetime import datetime
from coletor_seguidos import ColetorSeguro
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador import ClassificadorOdio

def log(etapa, status, msg=""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {etapa:20} | {status:8} | {msg}")

def main():
    # LER LIMITES DO AMBIENTE (Segurança contra 429)
    LIMITE_PERFIS = int(os.getenv('COLETA_LIMITE_PERFIS', 5))
    POSTS_POR_PERFIL = int(os.getenv('COLETA_POSTS_POR_PERFIL', 2))

    print(f"🚀 INICIANDO PIPELINE (Limite: {LIMITE_PERFIS} perfis, {POSTS_POR_PERFIL} posts/cada)\n")

    # 1. COLETA
    coletor = ColetorSeguro()
    df_bruto = coletor.coletar_todos_seguidos(
        posts_por_perfil=POSTS_POR_PERFIL, 
        limite_perfis=LIMITE_PERFIS
    )
    
    if df_bruto.empty:
        log("COLETA", "FALHA", "Sem dados coletados.")
        return

    # 2. PROCESSAMENTO E MINERAÇÃO
    proc = ProcessadorCorpus()
    df_proc, freq = proc.processar_dataframe(df_bruto)
    proc.gerar_nuvem_palavras(freq, salvar=True)
    
    miner = MineradorCorpus()
    miner.analisar_frequencia_ngrams(df_proc)

    # 3. CLASSIFICAÇÃO
    clas = ClassificadorOdio()
    df_final = clas.classificar_dataframe(df_proc)

    # 4. EXPORTAÇÃO PARA DASHBOARD
    dashboard_file = os.path.join("api", "dados_latest.csv")
    df_final.to_csv(dashboard_file, index=False, encoding='utf-8-sig')
    
    log("DASHBOARD", "PRONTO", f"Arquivo {dashboard_file} atualizado.")
    print("\n✅ PIPELINE CONCLUÍDO COM SUCESSO!")

if __name__ == "__main__":
    main()