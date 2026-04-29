# SENTINELA | Diamond Edition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the Sentinela platform into a robust data-driven intelligence tool with historical trends, network detection, and real-time alerts.

**Architecture:** Enhancing the current FastAPI + Supabase stack with historical metric persistence, materialized views for geo-aggregation, and a centralized frontend data service.

**Tech Stack:** Python (FastAPI, Pandas), PostgreSQL (Supabase/PostgREST), JavaScript (Vanilla), SQL (PL/pgSQL).

---

### Task 1: Database Schema Expansion

**Files:**
- Create: `scripts/diamond_schema_v1.sql`

- [ ] **Step 1: Create script for new tables and views**
  Write SQL to create `metricas_diarias`, `redes_coordenadas`, `alertas_ativos`, and the views `v_pasa_breakdown`, `v_candidato_score`.

- [ ] **Step 2: Execute SQL in Supabase**
  Use `execute_sql` (or manual run) to apply the schema.

- [ ] **Step 3: Verify table creation**
  Run: `SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';`
  Expected: All new tables exist.

---

### Task 2: Materialized Views & Triggers

**Files:**
- Modify: `scripts/diamond_schema_v1.sql` (append)

- [ ] **Step 1: Create materialized view `mv_agregacao_uf`**
  Add SQL for geo-aggregation by state.

- [ ] **Step 2: Create counter update trigger**
  Add SQL for `update_candidato_counters` and the trigger `trg_update_counters` on `comentarios`.

- [ ] **Step 3: Execute SQL in Supabase**
  Apply the changes.

---

### Task 3: Backend API - Trends & Geo Endpoints

**Files:**
- Modify: `api/index.py`

- [ ] **Step 1: Implement `/api/v1/trends`**
  Add endpoint to fetch historical metrics.

- [ ] **Step 2: Implement `/api/v1/pasa/breakdown`**
  Add endpoint to fetch PASA category distribution.

- [ ] **Step 3: Implement `/api/v1/geo/uf`**
  Add endpoint for map data.

- [ ] **Step 4: Verify endpoints**
  Run: `curl http://localhost:8000/api/v1/trends` (after starting server)
  Expected: JSON response with daily metrics.

---

### Task 4: Backend API - Networks, Alerts & Targets

**Files:**
- Modify: `api/index.py`

- [ ] **Step 1: Implement `/api/v1/networks`**
  Add endpoint for coordinated network data.

- [ ] **Step 2: Implement `/api/v1/alerts/active`**
  Add endpoint for active alerts.

- [ ] **Step 3: Upgrade `/api/v1/summary` and `/api/v1/targets`**
  Update existing endpoints to use new views and include trends.

---

### Task 5: Pipeline Persistence Logic

**Files:**
- Modify: `processing/data_miner.py`
- Modify: `orquestrador.py`

- [ ] **Step 1: Update `DataMiner` to return persistence data**
  Modify `analise_temporal` and `thematic_clustering` to return structured results.

- [ ] **Step 2: Add `persist_daily_metrics` to `Orchestrator`**
  Implement the function to upsert metrics at the end of the pipeline.

- [ ] **Step 3: Add `check_and_create_alerts` and `persist_networks`**
  Implement these in `Orchestrator` using data from `DataMiner`.

---

### Task 6: Frontend Data Service

**Files:**
- Create: `src/services/dataService.js` (Rewrite existing or create new)

- [ ] **Step 1: Implement `SentinelDataService` class**
  Create the service with methods for each new endpoint and cache logic.

- [ ] **Step 2: Export `dataService` instance**
  Ensure it's available for the UI components.

---

### Task 7: Frontend UI Integration

**Files:**
- Modify: `src/core/app.js`
- Modify: `src/core/ui.js`

- [ ] **Step 1: Replace mock data calls with `dataService`**
  Update `renderSummary`, `renderTriagem`, `renderMapa`, etc.

- [ ] **Step 2: Implement upgrade modal and plan gating**
  Add logic to mask names and block features for public users.

- [ ] **Step 3: Verify integration**
  Open `index.html` and check if data loads from the API.
