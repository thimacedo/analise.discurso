import argparse
import asyncio

from workers.collector import run_collection_once
from workers.kpi_orchestrator import sync_kpis_once


async def run_once() -> tuple[int, int]:
    collected = await run_collection_once()
    updated = await sync_kpis_once()
    return collected, updated


async def run_forever(interval_seconds: int = 900) -> None:
    print("[worker] sentinela collector iniciado")
    while True:
        try:
            collected, updated = await run_once()
            print(f"[worker] ciclo concluido: {collected} comentarios, {updated} candidatos atualizados")
        except Exception as exc:
            print(f"[worker] ciclo falhou: {str(exc)[:120]}")
        await asyncio.sleep(interval_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Worker oficial de coleta Sentinela")
    parser.add_argument("--once", action="store_true", help="Executa um ciclo unico")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.once:
        print(asyncio.run(run_once()))
    else:
        asyncio.run(run_forever())
