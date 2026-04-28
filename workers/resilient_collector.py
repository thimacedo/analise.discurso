import asyncio
import os
from datetime import datetime

import httpx

from workers.common import SUPABASE_URL, ensure_runtime_dirs, require_env, supabase_headers


BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY", "")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID", "")


async def get_raw_html_via_browserbase(url: str) -> list[dict]:
    if not BROWSERBASE_API_KEY or not BROWSERBASE_PROJECT_ID:
        return []

    headers = {"x-bb-api-key": BROWSERBASE_API_KEY, "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                "https://www.browserbase.com/v1/sessions",
                headers=headers,
                json={"projectId": BROWSERBASE_PROJECT_ID},
            )
            response.raise_for_status()
            return []
        except Exception:
            return []


async def run() -> None:
    ensure_runtime_dirs()
    require_env("SUPABASE_URL", SUPABASE_URL)
    async with httpx.AsyncClient() as client:
        targets_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/candidatos",
            params={"status_monitoramento": "eq.Ativo", "select": "id,username", "limit": 2},
            headers=supabase_headers(),
        )
        targets_response.raise_for_status()
        targets = targets_response.json() or []

        for target in targets:
            comments = await get_raw_html_via_browserbase(f"https://www.picuki.com/profile/{target['username']}")
            if not comments:
                continue
            payload = [{
                "id_externo": f"bb_{target['username']}_{datetime.now().timestamp()}_{index}",
                "candidato_id": target["id"],
                "texto_bruto": comment["text"],
                "autor_username": comment["user"],
                "post_id": "bb_stealth_collection",
                "processado_ia": False,
            } for index, comment in enumerate(comments) if comment.get("text")]
            await client.post(
                f"{SUPABASE_URL}/rest/v1/comentarios",
                headers=supabase_headers("resolution=merge-duplicates"),
                json=payload,
            )


if __name__ == "__main__":
    asyncio.run(run())
