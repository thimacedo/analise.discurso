import argparse
import asyncio
import subprocess
import os
import sys

# Garante que o diretório raiz está no path para importar o orquestrador
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

async def run_full_update():
    print("🚀 [WORKER] Iniciando Orquestrador Sentinela v18.5...")
    # Executa o orquestrador como subprocesso para isolamento
    process = subprocess.Popen(
        [sys.executable, "orquestrador.py"],
        cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')),
        stdout=sys.stdout,
        stderr=sys.stderr,
        shell=True
    )
    process.wait()
    return process.returncode

async def run_forever(interval_seconds: int = 43200): # Padrão: 12 horas (conforme workflow)
    print("🛡️ [WORKER] Sentinela v18.5 Operational (Daemon Mode)")
    while True:
        try:
            await run_full_update()
            print(f"💤 Ciclo concluído. Aguardando {interval_seconds}s...")
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
