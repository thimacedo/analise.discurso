import asyncio
from datetime import datetime

import httpx

from workers.common import SUPABASE_URL, ensure_runtime_dirs, require_env, supabase_headers


async def sync_kpis_once() -> int:
    ensure_runtime_dirs()
    require_env("SUPABASE_URL", SUPABASE_URL)

    updated = 0
    async with httpx.AsyncClient(timeout=30.0) as client:
        candidates_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/candidatos",
            params={"select": "id,username"},
            headers=supabase_headers(),
        )
        candidates_response.raise_for_status()
        candidates = candidates_response.json() or []

        for candidate in candidates:
            cid = candidate.get("id")
            if not cid:
                continue

            total_resp = await client.get(
                f"{SUPABASE_URL}/rest/v1/comentarios",
                params={"candidato_id": f"eq.{cid}", "select": "id"},
                headers=supabase_headers("count=exact"),
            )
            total_resp.raise_for_status()

            hate_resp = await client.get(
                f"{SUPABASE_URL}/rest/v1/comentarios",
                params={"candidato_id": f"eq.{cid}", "is_hate": "eq.true", "select": "id"},
                headers=supabase_headers("count=exact"),
            )
            hate_resp.raise_for_status()

            total = int((total_resp.headers.get("Content-Range") or "0/0").split("/")[-1])
            hate = int((hate_resp.headers.get("Content-Range") or "0/0").split("/")[-1])

            patch_resp = await client.patch(
                f"{SUPABASE_URL}/rest/v1/candidatos",
                params={"id": f"eq.{cid}"},
                json={
                    "comentarios_totais_count": total,
                    "comentarios_odio_count": hate,
                    "last_kpi_sync": datetime.utcnow().isoformat(),
                },
                headers=supabase_headers("return=minimal"),
            )
            patch_resp.raise_for_status()
            updated += 1

    return updated


if __name__ == "__main__":
    print(asyncio.run(sync_kpis_once()))
