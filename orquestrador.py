import sys
import os
import shutil
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Prioriza variáveis de ambiente do sistema (GitHub Actions)
# Carrega .env APENAS se existir (desenvolvimento local)
if os.path.exists('.env'):
    load_dotenv()

from coletor import ColetorSeguro
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador import ClassificadorOdio

def log(etapa, status, msg=""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {etapa:20} | {status:8} | {msg}")

def main():
    # Verifica credenciais antes de começar
    IG_USERNAME = os.getenv('IG_USERNAME')
    IG_PASSWORD = os.getenv('IG_PASSWORD')
    
    if not IG_USERNAME or not IG_PASSWORD:
        print("❌ ERRO: IG_USERNAME e IG_PASSWORD não foram encontrados.")
        print("   Configure no .env (local) ou nos Secrets do GitHub Actions.")
        sys.exit(1)

    # Lê limites configuráveis por variável de ambiente
    limite_perfis = int(os.getenv('COLETA_LIMITE_PERFIS', 5))
    posts_por_perfil = int(os.getenv('COLETA_POSTS_POR_PERFIL', 2))

    print(f"🚀 INICIANDO PIPELINE ANÁLISE DISCURSO")
    print(f"   Configuração: {limite_perfis} perfis, {posts_por_perfil} posts cada\n")

    # 1. COLETA
    coletor = ColetorSeguro(
        username=IG_USERNAME,
        password=IG_PASSWORD
    )
    
    df_bruto = coletor.coletar_todos_seguidos(
        posts_por_perfil=posts_por_perfil,
        limite_perfis=limite_perfis
    )
    
    if df_bruto.empty:
        log("COLETA", "FALHA", "Sem dados coletados.")
        return

    # 2. PROCESSAMENTO
    proc = ProcessadorCorpus()
    df_proc, freq = proc.processar_dataframe(df_bruto)
    proc.gerar_nuvem_palavras(freq, salvar=True)

    # 3. CLASSIFICAÇÃO (GERA is_hate_speech)
    clas = ClassificadorOdio()
    df_final = clas.classificar_dataframe(df_proc)
    
    # 4. MINERAÇÃO (AGORA TEM A COLUNA is_hate_speech)
    miner = MineradorCorpus()
    miner.analisar_frequencia_ngrams(df_final)

    # 4. EXPORTAÇÃO AUTOMÁTICA PARA DASHBOARD
    # Salva com timestamp para histórico local
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    hist_file = f"resultado_{ts}.csv"
    df_final.to_csv(hist_file, index=False, encoding='utf-8-sig')

    # Copia para a pasta api (onde a Vercel vai ler)
    dashboard_file = os.path.join("api", "dados_latest.csv")
    df_final.to_csv(dashboard_file, index=False, encoding='utf-8-sig')
    
    log("DASHBOARD", "PRONTO", f"Arquivo api/dados_latest.csv atualizado.")
    print("\n✅ TUDO PRONTO! Pipeline executado com sucesso.")

if __name__ == "__main__":
    main()