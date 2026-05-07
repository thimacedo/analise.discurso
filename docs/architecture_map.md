# Sentinela Democrática - Architecture Map

## 1. System Overview
The "Sentinela Democrática" project is a monorepo consisting of:
- **Frontend (SPA)**: React-based web interface.
- **Backend (API Proxy)**: FastAPI application deployed on Vercel.
- **Processing Workers**: Python-based background workers for data collection and analysis.
- **Database**: Supabase PostgreSQL.

The system is designed to monitor, classify (via PASA v16.4 protocol), and report hate speech and political violence.

## 2. Directory Structure
- `api/`: FastAPI endpoints (`index.py`, `v1/`). Functions as an API proxy. Must remain Vercel-compatible (serverless).
- `core/`: Core shared libraries, including the `db.py` Supabase client (`DatabaseClient`).
- `processing/`: Background python workers unified under a `BaseWorker` abstraction, with metrics collection via `workers_metrics.py`.
- `src/`: React Frontend, containing `components/`, `services/`, and `styles/`.

## 3. Data Flow
1. **Scraping/Processing**: Background Python workers extract data from social networks (e.g., Meta Ad Library).
2. **Storage**: Data is processed using the PASA protocol and saved into Supabase via `core/db.py` (utilizing batch `upsert` operations for performance).
3. **Serving**: The FastAPI application queries Supabase to dynamically calculate risks and compile KPIs.
4. **Consumption**: The React frontend (`src/services/apiService.js`) fetches data from the FastAPI endpoints to render the dashboard.

## 4. Key Conventions
- **Database Access**: Frontend never interacts directly with Supabase. All data flows through FastAPI. Processing workers use `core/db.py`.
- **Background Processing**: Use the `BaseWorker` class for all background tasks to ensure standard error handling and metrics collection.
- **Serverless API**: Avoid long-running processes in the `api/` endpoints as they are subject to Vercel timeout constraints. Heavy processing must be offloaded.