# orquestrador.py
import sys
import traceback
import pandas as pd
from datetime import datetime
from coletor import ColetorSeguro
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador import ClassificadorOdio

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

# -------------------- ETAPAS --------------------
def etapa_coleta(candidatos, posts_por_candidato=10):
    coletor = ColetorSeguro()
    df = coletor.coletar_multiplos_candidatos(candidatos, posts_por_candidato)
    if df.empty:
        raise Exception("Nenhum dado coletado.")
    return df

def etapa_preprocessamento(df, coluna_texto='texto'):
    processador = ProcessadorCorpus(modelo_spacy="pt_core_news_sm")
    df_proc, freq_dist = processador.processar_dataframe(df, coluna_texto)
    processador.gerar_nuvem_palavras(freq_dist, salvar=True)
    processador.salvar_corpus(df_proc)
    return df_proc, freq_dist

def etapa_mineracao(df_proc):
    minerador = MineradorCorpus()
    ngrams = minerador.analisar_frequencia_ngrams(df_proc, coluna_tokens='tokens', top_n=30)
    
    # Gerar nuvens de bigramas e trigramas
    if ngrams['bigramas']:
        minerador.gerar_nuvem_ngrams(ngrams['bigramas'], titulo="Bigramas mais frequentes", salvar=True)
    if ngrams['trigramas']:
        minerador.gerar_nuvem_ngrams(ngrams['trigramas'], titulo="Trigramas mais frequentes", salvar=True)
    
    # Salvar n-gramas em CSV
    pd.DataFrame(ngrams['bigramas']).to_csv("bigramas.csv", index=False, encoding='utf-8-sig')
    pd.DataFrame(ngrams['trigramas']).to_csv("trigramas.csv", index=False, encoding='utf-8-sig')
    return ngrams

def etapa_classificacao(df_proc):
    classificador = ClassificadorOdio()
    df_classificado = classificador.classificar_dataframe(df_proc, coluna_texto='texto_limpo')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_csv = f"corpus_classificado_{timestamp}.csv"
    df_classificado.to_csv(nome_csv, index=False, encoding='utf-8-sig')
    log("CLASSIFICACAO", "SUCESSO", f"Arquivo salvo: {nome_csv}")
    return df_classificado

def etapa_resumo(df_classificado):
    """Gera um resumo estatístico simples"""
    total = len(df_classificado)
    odio = df_classificado[df_classificado['categoria_odio'] != 'neutro']
    print("\n" + "="*50)
    print("📊 RESUMO FINAL DA ANÁLISE")
    print("="*50)
    print(f"Total de comentários analisados: {total}")
    print(f"Comentários com discurso de ódio: {len(odio)} ({len(odio)/total*100:.2f}%)")
    print("\nDistribuição por categoria:")
    for cat in sorted(df_classificado['categoria_odio'].unique()):
        if cat != 'neutro':
            qtd = (df_classificado['categoria_odio'] == cat).sum()
            print(f"  - {cat}: {qtd} comentários")
    print("="*50)

# -------------------- MAIN --------------------
def main():
    # Configuração dos candidatos
    CANDIDATOS = ["lulaoficial", "jairmessiasbolsonaro"]
    POSTS_POR_CANDIDATO = 3 # Reduzido para teste rápido

    print("\n🚀 INICIANDO PIPELINE FORENSE\n")

    # 1. Coleta
    df_bruto = executar_etapa("COLETA", etapa_coleta, CANDIDATOS, POSTS_POR_CANDIDATO)

    # 2. Pré-processamento
    df_proc, freq_dist = executar_etapa("PRE-PROCESSAMENTO", etapa_preprocessamento, df_bruto, 'texto')

    # 3. Mineração
    ngrams = executar_etapa("MINERAÇÃO", etapa_mineracao, df_proc)

    # 4. Classificação
    df_classificado = executar_etapa("CLASSIFICAÇÃO", etapa_classificacao, df_proc)

    # 5. Resumo
    etapa_resumo(df_classificado)

    print("\n✅ PIPELINE CONCLUÍDO COM SUCESSO!")

if __name__ == "__main__":
    main()
