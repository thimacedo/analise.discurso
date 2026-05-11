from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

# Mount static files for frontend
# Assuming public directory is at the root of the project
STATIC_DIR = os.path.join(os.path.dirname(__file__), '..', 'public')
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Logging Configuration ---
LOG_FILE_PATH = 'logs/worker.log'
MAX_LOG_LINES = 100

def get_last_n_log_lines(filepath: str, n: int) -> List[str]:
    """Reads the last N lines from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Read all lines and slice the last N
            lines = f.readlines()
            return lines[-n:]
    except FileNotFoundError:
        logging.warning(f"Log file not found: {filepath}")
        return ["Log file not found."]
    except Exception as e:
        logging.error(f"Error reading log file {filepath}: {e}")
        return [f"Error reading log file: {e}"]

# --- Supabase Mock (replace with actual Supabase client if available) ---
# For now, we'll use mock data for demonstration
def get_supabase_stats():
    """
    Mocks fetching statistics from Supabase.
    In a real scenario, this would query the Supabase database.
    """
    logging.info("Fetching stats from Supabase (mocked)...")
    # Mock data representing counts from different stages
    return {
        "total_records": 15000,
        "ai_pending": 2500,
        "mined_records": 12500
    }

# --- API Endpoints ---

@app.get("/")
async def read_root():
    """Serves the main frontend file (monitor.html)."""
    try:
        with open(os.path.join(STATIC_DIR, "monitor.html"), "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), media_type="text/html")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="monitor.html not found. Ensure it's in the public directory.")

@app.get("/api/monitor/status")
async def get_monitor_status():
    """
    Returns the overall system status including Supabase stats and recent logs.
    """
    try:
        supabase_stats = get_supabase_stats()
        log_lines = get_last_n_log_lines(LOG_FILE_PATH, MAX_LOG_LINES)

        return JSONResponse(content={
            "supabase_stats": supabase_stats,
            "recent_logs": log_lines
        })
    except Exception as e:
        logging.error(f"Error in /api/monitor/status: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# --- Health Check Endpoint ---
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --- Mock Supabase client to allow running the API locally without Supabase setup ---
# This part is crucial for local development if Supabase client is not directly importable
# You might need to adapt this based on how your Supabase client is initialized elsewhere.
# For this example, we'll assume a simple mock.

# Mock Supabase client if it's not available or to simulate responses
try:
    from core.db import supabase_client # Assuming this is where your supabase client is initialized
except ImportError:
    logging.warning("Supabase client not found. Using mock data for API.")
    # Define a mock object or function if the real client isn't available
    class MockSupabaseClient:
        def __init__(self):
            # Mock the database client and table access
            self.db = self.MockDatabase()

        class MockDatabase:
            def __init__(self):
                # Mock table objects with a 'select' method
                self.total_records_table = self.MockTable("total_records")
                self.ai_pending_table = self.MockTable("ai_pending")
                self.mined_records_table = self.MockTable("mined_records")

            def table(self, table_name):
                if table_name == 'total_records':
                    return self.total_records_table
                elif table_name == 'ai_pending':
                    return self.ai_pending_table
                elif table_name == 'mined_records':
                    return self.mined_records_table
                else:
                    raise ValueError(f"Mock table {table_name} not found")

            class MockTable:
                def __init__(self, name):
                    self.name = name

                def select(self, query="*"):
                    # Simulate fetching a count
                    if "count()" in query:
                        # Return mock counts
                        if self.name == 'total_records': return MockQuery(15000)
                        if self.name == 'ai_pending': return MockQuery(2500)
                        if self.name == 'mined_records': return MockQuery(12500)
                    return MockQuery(None) # Default mock response if not count

        def from_(self, table_name):
             return self.db.table(table_name)

    class MockQuery:
        def __init__(self, value):
            self._value = value
        
        def execute(self):
            # Simulate query execution returning a value
            return self.MockExecuteResult(self._value)

        class MockExecuteResult:
            def __init__(self, data):
                self.data = data

            def single(self):
                return self.data # Return the mock value directly

    supabase_client = MockSupabaseClient() # Instantiate the mock client

    # Override the get_supabase_stats function to use the mock client
    def get_supabase_stats():
        logging.info("Fetching stats from Supabase (mocked client)...")
        try:
            # Use the mock client to simulate Supabase calls
            total_res = supabase_client.from_('total_records').select("count()").execute().single()
            ai_pending_res = supabase_client.from_('ai_pending').select("count()").execute().single()
            mined_res = supabase_client.from_('mined_records').select("count()").execute().single()

            return {
                "total_records": total_res if total_res is not None else 0,
                "ai_pending": ai_pending_res if ai_pending_res is not None else 0,
                "mined_records": mined_res if mined_res is not None else 0
            }
        except Exception as e:
            logging.error(f"Mock Supabase fetch error: {e}")
            return {"error": str(e)}

# If you have a real Supabase client initialization in api/db.py,
# you might need to import and use it here. For demonstration,
# we assume the above mock handles the case where it's not available.
# Example of how it might look with a real client:
# from core.db import supabase_client
# @app.get("/api/monitor/status")
# async def get_monitor_status():
#     try:
#         # This is a hypothetical Supabase query. Adjust based on your schema.
#         total_res = supabase_client.table('records').select('count()').execute()
#         ai_pending_res = supabase_client.table('ai_queue').select('count()').execute()
#         mined_res = supabase_client.table('mined_data').select('count()').execute()
#
#         # ... rest of the logic ...
#     except Exception as e:
#         ...
