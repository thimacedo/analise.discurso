import sys
import os
import shutil
import traceback
from datetime import datetime
from coletor import ColetorSeguro
from processador import ProcessadorCorpus
from minerador import MineradorCorpus
from classificador import ClassificadorOdio

def log(etapa, status, msg=""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {etapa:20} | {status:8} | {msg}")

def main():
    print("🚀 INICIANDO PIPELINE (Fluxo Git-Local)\n")

    # 1. COLETA (MODO TESTE: APENAS 5 PERFIS INICIALMENTE)
    # Aumente limite_perfis gradualmente conforme o script funcionar sem erros 429
    coletor = ColetorSeguro()
    df_bruto = coletor.coletar_todos_seguidos(posts_por_perfil=3, limite_perfis=5)
    
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

    # 4. EXPORTAÇÃO AUTOMÁTICA PARA DASHBOARD
    # Salva com timestamp para histórico local
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    hist_file = f"resultado_{ts}.csv"
    df_final.to_csv(hist_file, index=False, encoding='utf-8-sig')

    # Copia para a pasta api (onde a Vercel vai ler)
    dashboard_file = os.path.join("api", "dados_latest.csv")
    df_final.to_csv(dashboard_file, index=False, encoding='utf-8-sig')
    
    log("DASHBOARD", "PRONTO", f"Arquivo api/dados_latest.csv atualizado.")
    print("\n✅ TUDO PRONTO! Agora rode: git add . ; git commit -m 'atualizar dados' ; git push")

if __name__ == "__main__":
    main()