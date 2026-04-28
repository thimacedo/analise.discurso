import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SENTINELA_SUPABASE_KEY") or ""
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY") or ""
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or ""
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_TRIAGE = os.getenv("MODEL_TRIAGE", "qwen2.5:3b")
MODEL_EXPERT = os.getenv("MODEL_EXPERT", "gemma:2b")


def ensure_runtime_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def require_env(name: str, value: str) -> str:
    if value:
        return value
    raise RuntimeError(f"Variavel obrigatoria ausente: {name}")


def supabase_headers(prefer: str | None = None) -> dict:
    key = require_env("SUPABASE_KEY", SUPABASE_KEY)
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if prefer:
        headers["Prefer"] = prefer
    return headers
