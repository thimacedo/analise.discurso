import sys
import traceback
from datetime import datetime
from coletor import ColetorSeguro

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

def main():
    print("=== ForenseNet | Orquestrador de Pipeline ===\n")
    
    # 1. COLETA (Executada pelo ColetorSeguro)
    # Substitua pelos candidatos que deseja monitorar
    candidatos_alvo = ["lulaoficial", "jairmessiasbolsonaro"] 
    
    coletor = ColetorSeguro()
    df_bruto = executar_etapa(
        "COLETA INSTAGRAM", 
        coletor.coletar_multiplos_candidatos, 
        lista_candidatos=candidatos_alvo, 
        posts_por_candidato=5
    )

    if df_bruto.empty:
        log_etapa("COLETA", "Vazio", "Nenhum comentário coletado. Encerrando.")
        return

    # 2. PRÉ-PROCESSAMENTO & MINERAÇÃO (A implementar nas próximas fases)
    # 3. CLASSIFICAÇÃO IA
    # 4. SINCRONIZAÇÃO CLOUD (S3)

    print("\n✅ Fluxo orquestrado concluído com sucesso.")

if __name__ == "__main__":
    main()
