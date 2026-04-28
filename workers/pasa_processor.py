import argparse
import asyncio
import json
from pathlib import Path

import httpx

from workers.common import DATA_DIR, GROQ_API_KEY, SUPABASE_URL, ensure_runtime_dirs, require_env, supabase_headers


LIVE_LOGS_FILE = DATA_DIR / "pasa_live_logs.json"


def emit_log(candidate: str, text: str, status: str, category: str) -> None:
    ensure_runtime_dirs()
    logs = []
    if LIVE_LOGS_FILE.exists():
        try:
            logs = json.loads(LIVE_LOGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            logs = []
    new_log = {
        "alvo": candidate,
        "texto": (text or "")[:60],
        "status": status,
        "categoria": category,
    }
    logs = [new_log] + logs[:4]
    LIVE_LOGS_FILE.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")


async def analyze_comment(text: str) -> dict | None:
    api_key = require_env("GROQ_API_KEY", GROQ_API_KEY)
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Voce e um perito em linguistica forense. "
                    "Responda JSON valido com as chaves is_hate, categoria_ia e justificativa."
                ),
            },
            {"role": "user", "content": f"Comentario: {text}"},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
        )
    response.raise_for_status()
    data = response.json()
    if "choices" not in data:
        return None
    return json.loads(data["choices"][0]["message"]["content"])


async def process_batch(limit: int = 10) -> int:
    require_env("SUPABASE_URL", SUPABASE_URL)
    async with httpx.AsyncClient(timeout=30.0) as client:
        fetch_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/comentarios",
            params={"processado_ia": "eq.false", "limit": limit, "order": "data_coleta.desc", "select": "*,candidatos(username)"},
            headers=supabase_headers(),
        )
        fetch_response.raise_for_status()
        comments = fetch_response.json() or []
        if not comments:
            return 0

        processed = 0
        for comment in comments:
            text = comment.get("texto_bruto") or comment.get("texto")
            if not text:
                continue
            try:
                result = await analyze_comment(text)
            except Exception as exc:
                print(f"[pasa] falha de classificacao {comment.get('id')}: {str(exc)[:80]}")
                continue
            if not result:
                continue

            is_hate = bool(result.get("is_hate"))
            category = result.get("categoria_ia") or result.get("categoria") or "NEUTRO"
            emit_log(
                comment.get("candidatos", {}).get("username") or str(comment.get("candidato_id")),
                text,
                "ALERTA" if is_hate else "NEUTRO",
                category,
            )

            patch_response = await client.patch(
                f"{SUPABASE_URL}/rest/v1/comentarios",
                params={"id": f"eq.{comment['id']}"},
                headers=supabase_headers("return=minimal"),
                json={
                    "processado_ia": True,
                    "is_hate": is_hate,
                    "categoria_ia": category,
                    "justificativa": result.get("justificativa", ""),
                },
            )
            patch_response.raise_for_status()
            processed += 1
            await asyncio.sleep(1)

        return processed


async def run_forever(poll_interval: int = 30) -> None:
    print("[pasa] worker iniciado")
    while True:
        try:
            count = await process_batch()
            await asyncio.sleep(poll_interval if count == 0 else 5)
        except Exception as exc:
            print(f"[pasa] ciclo falhou: {str(exc)[:120]}")
            await asyncio.sleep(10)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Worker PASA para classificacao no Supabase")
    parser.add_argument("--once", action="store_true", help="Processa um lote e encerra")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    ensure_runtime_dirs()
    if args.once:
        print(asyncio.run(process_batch()))
    else:
        asyncio.run(run_forever())
