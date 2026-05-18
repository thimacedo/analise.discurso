import subprocess
import time
from datetime import datetime
import os
import sys

def run_until_dawn(target_hour=6):
    print(f"🌖 [OPERADOR NOTURNO] Iniciando ciclo de vigilância...")
    print(f"⏰ Horário Alvo: {target_hour}:00 da manhã.")
    
    # Configura o PYTHONPATH para garantir que os módulos sejam encontrados
    env = os.environ.copy()
    env["PYTHONPATH"] = "."

    while True:
        now = datetime.now()
        
        # Se já passou das 6h e ainda não é meia-noite (para não parar se começar as 23h)
        if now.hour >= target_hour and now.hour < 12:
            print(f"☀️ Amanheceu! Horário atual: {now.strftime('%H:%M:%S')}. Encerrando Operação Long Scrape.")
            break
            
        print(f"\n🚀 [{now.strftime('%H:%M:%S')}] Iniciando novo lote de 5 alvos...")
        
        try:
            # Executa o orquestrador em lotes de 5 para manter o controle e métricas
            # Usando sys.executable para garantir o mesmo ambiente virtual
            result = subprocess.run(
                [sys.executable, "workers/orchestrator_long_run.py", "--limit", "5"],
                env=env,
                capture_output=False,
                text=True
            )
            
            if result.returncode != 0:
                print(f"⚠️ Aviso: O lote anterior retornou código de erro {result.returncode}. Continuando...")

        except Exception as e:
            print(f"❌ Erro ao disparar lote: {e}")

        # Pausa estratégica entre lotes (Inter-Batch Cool-down)
        # 60 segundos para evitar aquecimento da sessão do Instagram
        print("💤 Pausa estratégica de 60s entre lotes (Inter-Batch Cool-down)...")
        time.sleep(60)

if __name__ == "__main__":
    run_until_dawn(6)