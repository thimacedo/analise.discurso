
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os
from typing import List
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings:
    PROJECT_NAME: str = "Sentinela Democrática"
    VERSION: str = "20.5.7"
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # AI Cloud APIs
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_KEYS: List[str] = [k.strip() for k in os.getenv("GEMINI_API_KEYS", "").split(",") if k.strip()]
    
    # Se GEMINI_API_KEYS estiver vazio mas GEMINI_API_KEY tiver valor, popula a lista
    if not GEMINI_API_KEYS and GEMINI_API_KEY:
        GEMINI_API_KEYS = [GEMINI_API_KEY]
    
    # AI Local (Ollama)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    
    # AI Strategy
    IA_PROVIDER: str = os.getenv("IA_PROVIDER", "hybrid") # hybrid, gemini, groq, ollama
    
    # External APIs
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")
    META_API_VERSION: str = os.getenv("META_API_VERSION", "v19.0")
    
    # Security
    DASHBOARD_PIN: str = os.getenv("DASHBOARD_PIN", "1234")
    ADMIN_TOTP_SECRET: str = os.getenv("SENTINELA_ADMIN_TOTP_SECRET", "")

settings = Settings()
