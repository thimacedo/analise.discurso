"""
PASA v37.1 - Watchdog: O Guardião do Servidor com Alerta WhatsApp
Monitora o local_server.py, reinicia se travar e avisa o operador via CallMeBot.
"""
import time
import subprocess
import sys
import os
import requests

# Garante que o diretório raiz do projeto esteja no Python Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.auto_updater import check_for_updates

SERVER_SCRIPT = "local_server.py"
RESTART_DELAY = 30 # Segundos antes de ressuscitar

# Credenciais CallMeBot (Integrado no Watchdog para resiliência máxima)
CALLMEBOT_PHONE = "558496066876"
CALLMEBOT_APIKEY = "8552672"
CALLMEBOT_URL = "https://api.callmebot.com/whatsapp.php"

def send_whatsapp_alert(message: str):
    """Dispara alerta síncrono via WhatsApp usando CallMeBot."""
    try:
        params = {
            "phone": CALLMEBOT_PHONE,
            "apikey": CALLMEBOT_APIKEY,
            "text": message
        }
        # Nota: O CallMeBot espera que o texto esteja codificado, requests cuida disso nos params
        requests.get(CALLMEBOT_URL, params=params, timeout=10)
        print(f"[Watchdog] Alerta WhatsApp enviado: {message[:30]}...")
    except Exception as e:
        print(f"[Watchdog] Falha ao enviar alerta WhatsApp: {e}")

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
            last_update_check = time.time()
            
            while True:
                poll = process.poll()
                if poll is not None:
                    if poll == 0:
                        print("[Watchdog] Servidor encerrado normalmente (Código 0).")
                    else:
                        error_msg = f"🚨 *WATCHDOG ALERT* 🚨\n\nO *Servidor Sentinela* travou inesperadamente!\nCódigo de erro: `{poll}`\n\nO Watchdog vai reiniciá-lo em {RESTART_DELAY} segundos."
                        print(f"[Watchdog] ⚠️ Servidor travou com código {poll}! Notificando via WhatsApp e preparando para ressuscitar...")
                        send_whatsapp_alert(error_msg)
                    break
                
                # A cada 60 segundos de monitoramento, verifica se há uma diretiva remota
                current_time = time.time()
                if current_time - last_update_check > 60:
                    last_update_check = current_time
                    if check_for_updates():
                        print("[Watchdog] Diretiva de reinício remoto recebida. Encerrando processo atual...")
                        process.terminate()
                        process.wait()
                        break
                
                time.sleep(5) # Check de processo a cada 5s

        except Exception as e:
            print(f"[Watchdog] Erro ao gerenciar subprocesso: {e}")

        # 4. Se parou, espera um pouco e reinicia
        print(f"[Watchdog] Aguardando {RESTART_DELAY}s antes de reiniciar...")
        time.sleep(RESTART_DELAY)

if __name__ == "__main__":
    # Garante que o diretório de trabalho é a raiz do projeto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    guard()
