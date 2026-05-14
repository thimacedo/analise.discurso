# api/routes/monitor.py
from fastapi import APIRouter
from core.supabase_service import get_supabase_client
from datetime import datetime, UTC

router = APIRouter(prefix="/api/v1/monitor")


@router.get("/workers")
async def get_workers_dashboard():
    db = get_supabase_client()

    # Lê a view worker_health que criamos na migration
    try:
        health = db.table("worker_health").select("*").execute().data or []
    except:
        return {"error": "View worker_health não encontrada. Execute a migração SQL."}

    # Calcula agregados globais
    total_workers   = len(health)
    healthy_workers = sum(1 for w in health if (w.get("success_rate_pct") or 0) >= 80)
    total_items     = sum(w.get("total_items_processed") or 0 for w in health)
    total_runs      = sum(w.get("total_runs") or 0 for w in health)
    total_success   = sum(w.get("successes") or 0 for w in health)

    overall_rate = round(
        total_success / total_runs * 100, 1
    ) if total_runs else 0.0

    avg_throughput = round(
        sum(
            (w.get("total_items_processed") or 0) /
            max((w.get("avg_duration_ms") or 1000) / 1000, 1)
            for w in health
        ) / max(total_workers, 1),
        2,
    ) if total_workers else 0.0

    return {
        "timestamp":                       datetime.now(UTC).isoformat(),
        "total_workers":                   total_workers,
        "healthy_workers":                 healthy_workers,
        "degraded_workers":                total_workers - healthy_workers,
        "system_health":                   _system_health(healthy_workers, total_workers),
        "total_executions":                total_runs,
        "total_successful":                total_success,
        "overall_success_rate":            overall_rate,
        "total_items_processed":           total_items,
        "avg_system_throughput_items_per_sec": avg_throughput,
        "workers": [
            {
                "worker":                    w["worker_name"],
                "status":                    "healthy" if (w.get("success_rate_pct") or 0) >= 80 else "degraded",
                "total_executions":          w.get("total_runs") or 0,
                "success_rate":              w.get("success_rate_pct") or 0,
                "avg_duration_ms":           w.get("avg_duration_ms") or 0,
                "avg_throughput_items_per_sec": round(
                    (w.get("total_items_processed") or 0) /
                    max((w.get("avg_duration_ms") or 1000) / 1000, 1),
                    2,
                ),
                "total_items_processed":     w.get("total_items_processed") or 0,
                "last_run_at":               w.get("last_run_at"),
                "recent_errors":             [
                    {"error": e, "timestamp": w.get("last_run_at")}
                    for e in (w.get("recent_errors") or [])
                    if e
                ],
            }
            for w in health
        ],
    }


def _system_health(healthy: int, total: int) -> str:
    if total == 0:
        return "unknown"
    ratio = healthy / total
    if ratio >= 0.8:
        return "green"
    if ratio >= 0.5:
        return "yellow"
    return "red"
