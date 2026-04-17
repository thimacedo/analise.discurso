# worker_monitoramento.py
import time
import schedule
import subprocess
import os
import sys
from datetime import datetime

# Configuração do caminho do Python no ambiente virtual
VENV_PYTHON = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
PIPELINE_SCRIPT = os.path.join(os.getcwd(), "main_pipeline.py")

def executar_pipeline():
    print(f"\n" + "!"*60)
    print(f"🕒 INICIANDO COLETA AGENDADA: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("!"*60)
    
    try:
        # Executa o pipeline como um processo separado
        result = subprocess.run([VENV_PYTHON, PIPELINE_SCRIPT], capture_output=True, text=True)
        
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
