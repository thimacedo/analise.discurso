import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Sentinela Democrática"
    VERSION: str = "20.5.6"
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # AI Cloud APIs
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # AI Local (Ollama)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    
    # AI Strategy
    IA_PROVIDER: str = os.getenv("IA_PROVIDER", "hybrid") # hybrid, gemini, groq, ollama
    
    # External APIs
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")
    META_API_VERSION: str = os.getenv("META_API_VERSION", "v20.0")
    
    # Security
    DASHBOARD_PIN: str = os.getenv("DASHBOARD_PIN", "1234")
    ADMIN_TOTP_SECRET: str = os.getenv("SENTINELA_ADMIN_TOTP_SECRET", "")

settings = Settings()
