import asyncio
import logging

import httpx

from core.ai_engine import AIEngine
from workers.common import SUPABASE_URL, ensure_runtime_dirs, require_env, supabase_headers


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sentinela-Intelligence")
BATCH_SIZE = 10


async def process_batch() -> bool:
    ensure_runtime_dirs()
    require_env("SUPABASE_URL", SUPABASE_URL)
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/comentarios",
            params={"processado_ia": "eq.false", "limit": BATCH_SIZE},
            headers=supabase_headers(),
        )
        response.raise_for_status()
        comments = response.json() or []
        if not comments:
            logger.info("Fila vazia.")
            return False

        engine = AIEngine()
        for comment in comments:
            try:
                logger.info("Analisando %s", comment["id"])
                result = await engine.analyze_comment(comment["texto_bruto"])
                patch_response = await client.patch(
                    f"{SUPABASE_URL}/rest/v1/comentarios",
                    params={"id": f"eq.{comment['id']}"},
                    json={
                        "processado_ia": True,
                        "is_hate": result.get("is_hate", False),
                        "categoria_ia": result.get("categoria", "NEUTRO"),
                    },
                    headers=supabase_headers("return=minimal"),
                )
                patch_response.raise_for_status()
            except Exception as exc:
                logger.error("Erro no registro %s: %s", comment.get("id"), exc)

        return True


async def main() -> None:
    logger.info("Intelligence Worker legado iniciado.")
    while True:
        has_more = await process_batch()
        await asyncio.sleep(2 if has_more else 30)


if __name__ == "__main__":
    asyncio.run(main())
