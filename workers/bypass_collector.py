import asyncio
import re

import httpx

from workers.common import SUPABASE_URL, ensure_runtime_dirs, require_env, supabase_headers


async def scrape_picuki(username: str) -> list[str]:
    url = f"https://www.picuki.com/profile/{username}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return []
            captions = re.findall(r'<div class="photo-description">(.*?)</div>', response.text, re.DOTALL)
            return [caption.strip() for caption in captions if len(caption.strip()) > 10]
    except Exception:
        return []


async def run() -> None:
    ensure_runtime_dirs()
    require_env("SUPABASE_URL", SUPABASE_URL)
    async with httpx.AsyncClient() as client:
        targets_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/candidatos",
            params={"status_monitoramento": "eq.Ativo", "select": "id,username", "limit": 5},
            headers=supabase_headers(),
        )
        targets_response.raise_for_status()
        targets = targets_response.json() or []

        for target in targets:
            evidences = await scrape_picuki(target["username"])
            if not evidences:
                continue
            payload = [{
                "id_externo": f"bp_{target['username']}_{index}",
                "candidato_id": target["id"],
                "texto_bruto": evidence,
                "post_id": f"picuki_{target['username']}",
                "processado_ia": False,
            } for index, evidence in enumerate(evidences[:5])]
            await client.post(
                f"{SUPABASE_URL}/rest/v1/comentarios",
                headers=supabase_headers("resolution=merge-duplicates"),
                json=payload,
            )
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run())
