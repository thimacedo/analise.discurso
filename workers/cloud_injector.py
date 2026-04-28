import asyncio

from workers.kpi_orchestrator import sync_kpis_once


if __name__ == "__main__":
    print(asyncio.run(sync_kpis_once()))
