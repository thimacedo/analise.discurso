import sys
import traceback
from datetime import datetime
from coletor import ColetorSeguro
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador import ClassificadorOdio

def log_etapa(etapa, status, mensagem=""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {etapa:.<25} {status:.<10} {mensagem}")

def executar_etapa(nome, funcao, *args, **kwargs):
    log_etapa(nome, "INICIADO")
    try:
        res = funcao(*args, **kwargs)
        log_etapa(nome, "SUCESSO")
        return res
    except Exception:
        log_etapa(nome, "FALHA")
        traceback.print_exc()
        sys.exit(1)

def main():
    print("="*50)
    print("   FORENSENET | PIPELINE DE ANÁLISE POLÍTICA")
    print("="*50 + "\n")

    # 1. COLETA
    candidatos = ["lulaoficial", "jairmessiasbolsonaro"] # Exemplo
    coletor = ColetorSeguro()
    df_bruto = executar_etapa("COLETA INSTAGRAM", coletor.coletar_multiplos_candidatos, candidatos, posts_por_candidato=3)
    
    if df_bruto.empty: return

    # 2. PROCESSAMENTO
    proc = ProcessadorCorpus()
    df_proc, frequencias = executar_etapa("PRÉ-PROCESSAMENTO", proc.processar_dataframe, df_bruto)

    # 3. MINERAÇÃO
    miner = MineradorCorpus()
    executar_etapa("MINERAÇÃO (NUVEM)", miner.gerar_nuvem_geral, frequencias)
    ngrams = executar_etapa("MINERAÇÃO (N-GRAMAS)", miner.analisar_frequencia_ngrams, df_proc)

    # 4. CLASSIFICAÇÃO
    clas = ClassificadorOdio()
    df_final = executar_etapa("CLASSIFICAÇÃO DE ÓDIO", clas.processar_dataframe, df_proc)

    # 5. SALVAMENTO
    fname = f"resultado_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df_final.to_csv(fname, index=False, encoding='utf-8-sig')
    log_etapa("EXPORTAÇÃO", "CONCLUÍDO", f"Relatório salvo em {fname}")

    print("\n✅ Fluxo Forense concluído com sucesso.")

if __name__ == "__main__":
    main()
