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
    
    if process.returncode == 0:
        print("💾 [WORKER] Sincronizando dados rastreados com o Source Control (Vercel Deploy Trigger)...")
        try:
            # Força o commit dos arquivos vitais de dados gerados
            subprocess.run(["git", "add", "api/dados_latest.csv", "visualizacoes/nuvem_geral.png"], check=False)
            commit_res = subprocess.run(["git", "commit", "-m", "data: autoupdate via worker contínuo"], capture_output=True, text=True)
            if "nothing to commit" not in commit_res.stdout:
                subprocess.run(["git", "push", "origin", "main"], check=False)
                print("☁️ [WORKER] Dados enviados para a nuvem! Deploy da Vercel iniciado.")
            else:
                print("📭 [WORKER] Nenhum dado novo para comitar.")
        except Exception as e:
            print(f"⚠️ [WORKER] Erro ao sincronizar dados com o Git: {e}")

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
