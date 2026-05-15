"""
PASA v37 - Watchdog: O Guardião do Servidor.
Monitora o local_server.py, reinicia se travar e aplica auto-evoluções.
"""
import time
import subprocess
import sys
import os

# Garante que o diretório raiz do projeto esteja no Python Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.auto_updater import check_for_updates

SERVER_SCRIPT = "local_server.py"
RESTART_DELAY = 30 # Segundos antes de ressuscitar

def guard():
    print("🐕 Watchdog Sentinela ativado. Guardando o Nó Local.")
    
    while True:
        # 1. Verifica se há atualizações de código ou config antes de iniciar
        print("[Watchdog] Verificando atualizações e diretivas remotas...")
        try:
            if check_for_updates():
                print("[Watchdog] Atualização detectada. O servidor reiniciará com o novo código.")
        except Exception as e:
            print(f"[Watchdog] Erro ao verificar atualizações: {e}")
        
        # 2. Inicia o servidor como um subprocesso
        print(f"[Watchdog] Iniciando {SERVER_SCRIPT}...")
        try:
            # Usando sys.executable para garantir que usa o mesmo interpretador Python
            process = subprocess.Popen([sys.executable, SERVER_SCRIPT])

            # 3. Monitora o processo
            while True:
                poll = process.poll()
                if poll is not None:
                    if poll == 0:
                        print("[Watchdog] Servidor encerrado normalmente (Código 0).")
                    else:
                        print(f"[Watchdog] ⚠️ Servidor travou com código {poll}! Preparando para ressuscitar...")
                    break
                
                # A cada minuto de monitoramento, verifica se há uma diretiva de RESTART ou UPDATE
                # Isso permite que o servidor seja reiniciado mesmo se não travar
                # Mas para simplificar o controle de logs, o check_for_updates aqui só deve
                # disparar o encerramento do processo atual se retornar True.
                time.sleep(60) 
                if check_for_updates():
                    print("[Watchdog] Diretiva de reinício remoto recebida. Encerrando processo atual...")
                    process.terminate()
                    process.wait()
                    break

        except Exception as e:
            print(f"[Watchdog] Erro ao gerenciar subprocesso: {e}")

        # 4. Se parou, espera um pouco e reinicia
        print(f"[Watchdog] Aguardando {RESTART_DELAY}s antes de reiniciar...")
        time.sleep(RESTART_DELAY)

if __name__ == "__main__":
    # Garante que o diretório de trabalho é a raiz do projeto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    guard()
