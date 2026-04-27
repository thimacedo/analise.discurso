import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Sentinela API"
    VERSION: str = "16.0.0"
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    
    # External APIs
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    RAPIDAPI_KEY: str = os.getenv("RAPIDAPI_KEY", "")
    
    # Security
    DASHBOARD_PIN: str = os.getenv("DASHBOARD_PIN", "1234")
    ADMIN_TOTP_SECRET: str = os.getenv("SENTINELA_ADMIN_TOTP_SECRET", "")

settings = Settings()
