
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from fastapi import APIRouter, HTTPException
import os
from core.config import settings
from core.supabase_service import supabase

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "worker.log")
MAX_LOG_LINES = 50 

def get_last_n_log_lines(filepath: str, n: int) -> list[str]:
    """Reads the last N lines from a file."""
    try:
        if not os.path.exists(filepath):
             return ["Log file not found."]
        
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return lines[-n:]
    except Exception as e:
        return [f"Error reading log file: {e}"]

@router.get("/status")
async def get_monitor_status():
    """
    Fetches status from Supabase and reads logs.
    """
    try:
        # Busca contagens REAIS no Supabase
        total_req = supabase.table("comentarios").select("id", count="exact").execute()
        pendentes_req = supabase.table("comentarios").select("id", count="exact").eq("processado_ia", False).execute()
        processados_req = supabase.table("comentarios").select("id", count="exact").eq("processado_ia", True).execute()
        
        total = total_req.count if hasattr(total_req, 'count') and total_req.count is not None else 0
        pendentes = pendentes_req.count if hasattr(pendentes_req, 'count') and pendentes_req.count is not None else 0
        processados = processados_req.count if hasattr(processados_req, 'count') and processados_req.count is not None else 0

    except Exception as e:
        print(f"Error fetching from Supabase: {e}")
        total, pendentes, processados = 0, 0, 0
    
    # Independente do DB, tenta ler os logs reais
    logs = get_last_n_log_lines(LOG_FILE_PATH, MAX_LOG_LINES)
        
    return {
        "total": total,
        "pendentes": pendentes,
        "processados": processados,
        "logs": logs
    }
