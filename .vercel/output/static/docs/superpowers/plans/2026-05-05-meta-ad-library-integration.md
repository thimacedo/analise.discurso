# Meta Ad Library Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a resilient collection, classification (PASA v16.4), and visualization system for political advertisements from the Meta Ad Library, ensuring the project has real-time data for the 2026 elections.

**Architecture:** Hybrid collection (Official API with Playwright Scraper fallback) -> SQL Persistence (Supabase) -> AI Analysis (PASA v16.4) -> Dashboard Visualization.

**Tech Stack:** Python (Playwright, HTTPX), Supabase (PostgreSQL), Gemini/Ollama (PASA Protocol).

---

### Task 1: Environment & Configuration Setup

**Files:**
- Modify: `.env.example`
- Modify: `core/config.py`

- [ ] **Step 1: Update .env.example with Meta variables**
Add `META_ACCESS_TOKEN` and `META_API_VERSION` (v19.0 as default).

- [ ] **Step 2: Update core/config.py to load Meta variables**
Ensure the `Settings` class includes these new variables.

- [ ] **Step 3: Commit**
```bash
git add .env.example core/config.py
git commit -m "feat(config): add meta ads environment variables"
```

---

### Task 2: Database Schema Validation

**Files:**
- Run: `scripts/migration_v22.1_anuncios_pasa.sql`
- Create: `scripts/verify_anuncios_schema.sql`

- [ ] **Step 1: Verify current schema**
Run a query to check if the `anuncios` table has the required PASA fields (`categoria_ia`, `is_hate`, etc.).

- [ ] **Step 2: Apply migration if missing**
Use the Supabase SQL editor or a local script to ensure columns exist.

- [ ] **Step 3: Commit**
```bash
git add scripts/verify_anuncios_schema.sql
git commit -m "fix(db): ensure anuncios table schema matches PASA v16.4"
```

---

### Task 3: Resilient Scraper & Service Refactoring

**Files:**
- Modify: `core/meta_ad_service.py`
- Modify: `core/meta_ad_scraper.py`

- [ ] **Step 1: Add fallback logic to MetaAdService**
Update `search_ads` to return an empty list gracefully if the token is missing, instead of just logging a warning.

- [ ] **Step 2: Improve MetaAdScraper selectors**
Update Playwright selectors in `_extract_card_data` to be more robust against Meta's DOM changes (use test-ids or more stable classes if available).

- [ ] **Step 3: Test collection locally**
Create a small script `scripts/test_collection_meta.py` that tries API first, then Scraper.

- [ ] **Step 4: Commit**
```bash
git add core/meta_ad_service.py core/meta_ad_scraper.py scripts/test_collection_meta.py
git commit -m "feat(collect): implement hybrid collection with scraper fallback"
```

---

### Task 4: Orchestrator Integration (The Missing Link)

**Files:**
- Modify: `core/orquestrador.py`

- [ ] **Step 1: Connect QueueManager to Ads Collection**
Update `run_meta_ads_cycle` to fetch targets from the same Supabase table as the main scraper (`fila_coleta`) instead of the static `priority_queue.json`.

- [ ] **Step 2: Implement Scraper Fallback in Orchestrator**
If `meta_ad_service.search_ads` returns 0 results and no token is present, call `meta_ad_scraper.scrape_ads_for_target`.

- [ ] **Step 3: Commit**
```bash
git add core/orquestrador.py
git commit -m "feat(orchestrator): integrate meta ads with target queue and scraper fallback"
```

---

### Task 5: End-to-End Validation (Diamond Standard)

**Files:**
- Run: `scripts/test_meta_full_cycle.py`

- [ ] **Step 1: Remove mocks from the test cycle**
Update `scripts/test_meta_full_cycle.py` to allow real DB writes (using a test flag) and real scraper execution.

- [ ] **Step 2: Run full cycle**
`python scripts/test_meta_full_cycle.py`
Expected: Real ads in Supabase, classified by AI.

- [ ] **Step 3: Update STATE.md**
Mark STN-003 as "Operacional".

- [ ] **Step 4: Final Commit**
```bash
git add scripts/test_meta_full_cycle.py STATE.md
git commit -m "feat(meta): finalize meta ad library integration"
```
