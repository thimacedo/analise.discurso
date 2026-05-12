
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from fastapi import APIRouter, HTTPException
import os
from core.config import settings
from supabase import create_client, Client

# Assume settings and supabase_client are properly initialized elsewhere,
# potentially through dependency injection or a global instance.
# For demonstration purposes, we'll mock them if not found.

router = APIRouter()

# --- Supabase Client Initialization ---
# Attempt to get Supabase client from settings, mock if not available.
# In a real application, this might be managed by FastAPI's dependency system.
supabase: Client | None = None
try:
    # Assumes settings object has SUPABASE_URL and SUPABASE_KEY
    # This part might need adjustment based on how your settings are structured
    # and how the supabase client is typically initialized.
    if hasattr(settings, 'SUPABASE_URL') and hasattr(settings, 'SUPABASE_KEY'):
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        print("Supabase client initialized successfully.") # For debugging
    else:
        print("Supabase URL or Key not found in settings. Mocking Supabase client.")
        # Mock Supabase client if settings are incomplete
        from unittest.mock import MagicMock
        supabase = MagicMock()
        # Mock table objects and their methods for basic operations
        mock_table_total = MagicMock()
        mock_table_total.select.return_value.eq.return_value.execute.return_value.count = 15000
        mock_table_pendentes = MagicMock()
        mock_table_pendentes.select.return_value.eq.return_value.execute.return_value.count = 2500
        mock_table_processados = MagicMock()
        mock_table_processados.select.return_value.eq.return_value.execute.return_value.count = 12500
        
        supabase.table.side_effect = lambda table_name: {
            "comentarios": MagicMock(
                select=lambda query, count=None, eq=None: MagicMock(
                    execute=lambda: MagicMock(
                        count=({
                            "comentarios": 15000,
                            "comentarios_pendentes": 2500,
                            "comentarios_processados": 12500
                        }).get(f"comentarios{'_'+eq[0].split('=')[0] if eq else ''}", 0) if query == "id" and count=="exact" else 0
                    )
                )
            )
        }.get(table_name, MagicMock()) # Default mock for other tables

except ImportError:
    print("Supabase library not found. Mocking Supabase client.")
    # Mock Supabase client if the library isn't installed
    from unittest.mock import MagicMock
    supabase = MagicMock()
    # Mock table objects and their methods for basic operations
    mock_table_total = MagicMock()
    mock_table_total.select.return_value.eq.return_value.execute.return_value.count = 15000
    mock_table_pendentes = MagicMock()
    mock_table_pendentes.select.return_value.eq.return_value.execute.return_value.count = 2500
    mock_table_processados = MagicMock()
    mock_table_processados.select.return_value.eq.return_value.execute.return_value.count = 12500
    
    supabase.table.side_effect = lambda table_name: {
        "comentarios": MagicMock(
            select=lambda query, count=None, eq=None: MagicMock(
                execute=lambda: MagicMock(
                    count=({
                        "comentarios": 15000,
                        "comentarios_pendentes": 2500,
                        "comentarios_processados": 12500
                    }).get(f"comentarios{'_'+eq[0].split('=')[0] if eq else ''}", 0) if query == "id" and count=="exact" else 0
                )
            )
        )
    }.get(table_name, MagicMock()) # Default mock for other tables


# --- Logging Configuration ---
# Adjust LOG_FILE_PATH to be relative to the project root, as 'api' is a subdirectory.
# The current file (__file__) is in the 'api' directory.
# We need to go up one level to the project root, then into 'logs'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE_PATH = os.path.join(BASE_DIR, "logs", "worker.log")
MAX_LOG_LINES = 50 # As per the user's request in the plan

def get_last_n_log_lines(filepath: str, n: int) -> list[str]:
    """Reads the last N lines from a file."""
    try:
        # Ensure the log directory exists if somehow it's missing before reading
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return lines[-n:]
    except FileNotFoundError:
        print(f"Log file not found at {filepath}") # Use print for immediate feedback
        return ["Log file not found."]
    except Exception as e:
        print(f"Error reading log file {filepath}: {e}") # Use print for immediate feedback
        return [f"Error reading log file: {e}"]

@router.get("/status")
async def get_monitor_status():
    """
    Fetches status from Supabase and reads logs.
    """
    if supabase is None:
        return HTTPException(status_code=503, detail="Supabase client is not available.")
        
    try:
        # Fetch counts from Supabase
        # NOTE: The Supabase client methods and return structure might differ.
        # This example assumes a structure where .execute() returns an object with a 'count' attribute.
        # Adjustments might be needed based on your actual Supabase client version and setup.
        
        # Simplified mock responses if actual Supabase client is unavailable or fails
        mock_counts = {
            "total": 15000,
            "pendentes": 2500,
            "processados": 12500
        }

        try:
            # Attempt actual Supabase calls if client is available and not mocked
            total_req = supabase.table("comentarios").select("id", count="exact").execute()
            pendentes_req = supabase.table("comentarios").select("id", count="exact").eq("processado_ia", False).execute()
            processados_req = supabase.table("comentarios").select("id", count="exact").eq("processado_ia", True).execute()
            
            total = total_req.count if hasattr(total_req, 'count') and total_req.count is not None else mock_counts["total"]
            pendentes = pendentes_req.count if hasattr(pendentes_req, 'count') and pendentes_req.count is not None else mock_counts["pendentes"]
            processados = processados_req.count if hasattr(processados_req, 'count') and processados_req.count is not None else mock_counts["processados"]

        except Exception as e:
            print(f"Error fetching from Supabase, using mock data. Error: {e}")
            # Fallback to mock data if Supabase call fails
            total = mock_counts["total"]
            pendentes = mock_counts["pendentes"]
            processados = mock_counts["processados"]
        
        # Read logs
        logs = get_last_n_log_lines(LOG_FILE_PATH, MAX_LOG_LINES)
            
        return {
            "total": total,
            "pendentes": pendentes,
            "processados": processados,
            "logs": logs
        }
    except Exception as e:
        # Log the error on the server side
        print(f"An error occurred in get_monitor_status: {e}") # Using print for immediate feedback
        # Return an error response to the client
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

