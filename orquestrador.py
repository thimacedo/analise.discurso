import sys
import traceback
from datetime import datetime
from coletor import ColetorSeguro
from processador import ProcessadorCorpus

def log_etapa(etapa, status, mensagem=""):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {etapa:.<20} {status:.<10} {mensagem}")

def executar_etapa(nome, funcao, *args, **kwargs):
    log_etapa(nome, "INICIADO")
    try:
        resultado = funcao(*args, **kwargs)
        log_etapa(nome, "SUCESSO")
        return resultado
    except Exception as e:
        log_etapa(nome, "FALHA", str(e))
        traceback.print_exc()
        sys.exit(1)

def fase_processamento(df):
    """Integração da Etapa 2: Processamento do Corpus"""
    proc = ProcessadorCorpus()
    df_proc, freq = proc.processar_dataframe(df)
    proc.gerar_nuvem_palavras(freq)
    proc.salvar_corpus(df_proc)
    return df_proc, freq

def main():
    print("=== ForenseNet | Orquestrador de Pipeline ===\n")
    
    # ETAPA 1: COLETA
    candidatos_alvo = ["lulaoficial", "jairmessiasbolsonaro"] 
    coletor = ColetorSeguro()
    df_bruto = executar_etapa(
        "COLETA INSTAGRAM", 
        coletor.coletar_multiplos_candidatos, 
        lista_candidatos=candidatos_alvo, 
        posts_por_candidato=3 # Reduzido para teste rápido
    )

    if df_bruto.empty:
        log_etapa("COLETA", "AVISO", "Nenhum dado coletado.")
        return

    # ETAPA 2: PRÉ-PROCESSAMENTO
    df_processado, frequencias = executar_etapa(
        "PROCESSAMENTO",
        fase_processamento,
        df_bruto
    )

    # PRÓXIMAS ETAPAS:
    # 3. Classificação de Ódio (IA)
    # 4. Sincronização Cloud

    print("\n✅ Fluxo orquestrado concluído com sucesso.")

if __name__ == "__main__":
    main()
