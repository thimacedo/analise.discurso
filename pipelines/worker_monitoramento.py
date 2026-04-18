# worker_monitoramento.py
import time
import schedule
import subprocess
import os
import sys
from datetime import datetime

# Configuração robusta de caminhos absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")
PIPELINE_SCRIPT = os.path.join(BASE_DIR, "main_pipeline.py")

def executar_pipeline():
    print(f"\n" + "!"*60)
    print(f"🕒 INICIANDO COLETA AGENDADA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📂 Script: {PIPELINE_SCRIPT}")
    print("!"*60)
    
    try:
        # Verifica se os arquivos existem antes de tentar rodar
        if not os.path.exists(VENV_PYTHON):
            print(f"❌ Erro: Python do ambiente virtual não encontrado em: {VENV_PYTHON}")
            return
            
        # Executa o pipeline como um processo separado, mantendo o diretório de trabalho
        result = subprocess.run([VENV_PYTHON, PIPELINE_SCRIPT], capture_output=True, text=True, cwd=BASE_DIR)
        
        if result.returncode == 0:
            print("✅ Pipeline executado com sucesso pelo Worker.")
            # Aqui poderíamos disparar um log para o banco ou um alerta no Telegram
        else:
            print(f"❌ Erro na execução do pipeline: {result.stderr}")
            
    except Exception as e:
        print(f"⚠️ Falha crítica no Worker: {e}")

def iniciar_agendamento():
    print("="*60)
    print("🤖 WORKER DE MONITORAMENTO FORENSENET ATIVO")
    print(f"Agendamento: A cada 6 horas")
    print("Pressione Ctrl+C para encerrar")
    print("="*60)

    # Agendar a cada 6 horas
    schedule.every(6).hours.do(executar_pipeline)
    
    # Executa uma vez agora na inicialização
    executar_pipeline()

    while True:
        schedule.run_pending()
        time.sleep(60) # Verifica a cada minuto

if __name__ == "__main__":
    iniciar_agendamento()
