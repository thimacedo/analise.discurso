import argparse
import asyncio
import subprocess
import os
import sys

# Garante que o diretório raiz está no path para importar o orquestrador
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

async def run_full_update():
    print("🚀 [WORKER] Iniciando Orquestrador Sentinela v20.5.1...")
    # Executa o orquestrador como subprocesso para isolamento
    process = subprocess.Popen(
        [sys.executable, "orquestrador.py"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
        stdout=sys.stdout,
        stderr=sys.stderr,
        shell=False # Removido shell=True por segurança e evitar subprocessos zumbis no Windows
    )
    process.wait()
    return process.returncode

async def run_forever(interval_seconds: int = 180): # Reduzido de 12 horas para 3 minutos (Constante)
    print("🛡️ [WORKER] Sentinela v20.5.1 Operational (Constant Parallel Mode)")
    while True:
        try:
            await run_full_update()
            print(f"💤 Ciclo concluído. O motor vai resfriar por {interval_seconds}s antes da próxima raspagem...")
        except Exception as exc:
            print(f"⚠️ Erro crítico no worker: {exc}")
        await asyncio.sleep(interval_seconds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    if args.once:
        asyncio.run(run_full_update())
    else:
        asyncio.run(run_forever())
