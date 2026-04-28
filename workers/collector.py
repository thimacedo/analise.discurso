import asyncio
import time

import httpx

from workers.common import RAPIDAPI_KEY, SUPABASE_URL, ensure_runtime_dirs, require_env, supabase_headers


class APIStrategy:
    def __init__(self, host: str, name: str):
        self.host = host
        self.name = name
        self.failure_count = 0
        self.cooldown_until = 0.0

    def mark_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= 3:
            self.cooldown_until = time.time() + 900

    def available(self) -> bool:
        if self.cooldown_until and time.time() > self.cooldown_until:
            self.failure_count = 0
            self.cooldown_until = 0.0
        return self.cooldown_until == 0.0


class LoadBalancer:
    def __init__(self):
        self.strategies = [
            APIStrategy("instagram-scrapper-new.p.rapidapi.com", "Scraper-New"),
            APIStrategy("instagram-public-bulk-scraper.p.rapidapi.com", "Bulk-Scraper"),
            APIStrategy("instagram-scraper-20251.p.rapidapi.com", "Scraper-20251"),
        ]
        self.current = 0

    def next_strategy(self) -> APIStrategy | None:
        for _ in range(len(self.strategies)):
            strategy = self.strategies[self.current]
            self.current = (self.current + 1) % len(self.strategies)
            if strategy.available():
                return strategy
        return None


def rapidapi_headers(host: str) -> dict:
    key = require_env("RAPIDAPI_KEY", RAPIDAPI_KEY)
    return {
        "x-rapidapi-key": key,
        "x-rapidapi-host": host,
        "Content-Type": "application/json",
    }


async def collect_target(client: httpx.AsyncClient, target: dict, strategy: APIStrategy) -> int:
    username = target["username"]
    candidate_id = target["id"]
    print(f"[-] @{username} via {strategy.name}")

    try:
        feed_response = await client.post(
            f"https://{strategy.host}/getFeedByUsername",
            json={"username": username},
            headers=rapidapi_headers(strategy.host),
            timeout=20.0,
        )
        if feed_response.status_code == 429:
            strategy.mark_failure()
            return 0
        feed_response.raise_for_status()

        posts = (feed_response.json().get("data") or [])[:2]
        if not posts:
            return 0

        inserted = 0
        for post in posts:
            media_id = post.get("id")
            if not media_id:
                continue
            comments_response = await client.post(
                f"https://{strategy.host}/getMediaComments",
                json={"media_id": media_id},
                headers=rapidapi_headers(strategy.host),
                timeout=20.0,
            )
            comments_response.raise_for_status()
            comments = (comments_response.json().get("comments") or [])[:10]

            payload = [{
                "id_externo": str(comment.get("id")),
                "candidato_id": candidate_id,
                "texto_bruto": comment.get("text"),
                "autor_username": comment.get("owner", {}).get("username"),
                "fonte_coleta": strategy.host,
                "processado_ia": False,
            } for comment in comments if comment.get("id") and comment.get("text")]

            if not payload:
                continue

            await client.post(
                f"{require_env('SUPABASE_URL', SUPABASE_URL)}/rest/v1/comentarios",
                json=payload,
                headers=supabase_headers("resolution=merge-duplicates"),
                timeout=30.0,
            )
            inserted += len(payload)

        strategy.failure_count = 0
        print(f"  [✓] @{username} finalizado com {inserted} comentarios.")
        return inserted
    except Exception as exc:
        print(f"  [!] Falha em @{username}: {str(exc)[:80]}")
        strategy.mark_failure()
        return 0


async def run_collection_once() -> int:
    ensure_runtime_dirs()
    require_env("SUPABASE_URL", SUPABASE_URL)
    require_env("SUPABASE_KEY", supabase_headers()["apikey"])
    require_env("RAPIDAPI_KEY", RAPIDAPI_KEY)

    lb = LoadBalancer()
    inserted_total = 0
    async with httpx.AsyncClient() as client:
        targets_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/candidatos",
            params={"status_monitoramento": "eq.Ativo", "select": "id,username"},
            headers=supabase_headers(),
            timeout=20.0,
        )
        targets_response.raise_for_status()
        targets = targets_response.json() or []

        batch_size = 6
        for start in range(0, len(targets), batch_size):
            batch = targets[start:start + batch_size]
            tasks = []
            for target in batch:
                strategy = lb.next_strategy()
                if strategy:
                    tasks.append(collect_target(client, target, strategy))
            if tasks:
                results = await asyncio.gather(*tasks)
                inserted_total += sum(results)
                await asyncio.sleep(5)

    return inserted_total


if __name__ == "__main__":
    total = asyncio.run(run_collection_once())
    print(f"[collector] comentarios inseridos: {total}")
