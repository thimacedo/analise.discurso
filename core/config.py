# api/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DASHBOARD_PIN = os.getenv("DASHBOARD_PIN", "1234")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

IS_VERCEL = os.getenv("VERCEL") or os.getenv("VERCEL_ENV")
