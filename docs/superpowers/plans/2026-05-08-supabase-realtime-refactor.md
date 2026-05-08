# Documentação e Refatoração da Integração Supabase Realtime - Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Documentar o erro de Supabase Realtime, modularizar a interação com o Supabase, e melhorar a documentação geral do código relacionado. Adicionalmente, investigar problemas de frontend relacionados à timeline e KPIs.

**Architecture:** A refatoração focará em isolar as interações com o Supabase em módulos dedicados, melhorar o tratamento de erros no script `fetch_pending.py`, e documentar a configuração do Realtime. Investigaremos também a lógica frontend para timeline e KPIs.

**Tech Stack:** Python, Supabase CLI, PostgREST, PostgreSQL, JavaScript/HTML (Frontend).

---

### Task 1: Documentar Detalhadamente o Erro Supabase Realtime

**Files:**
- Modify: `STATE.md`
- Create: `docs/supase-realtime-troubleshooting.md`

- [DONE] **Step 1: Review and consolidate current `STATE.md` documentation.**
    * Ensure all steps taken, error codes, function signatures checked, and attempted solutions are clearly listed.

- [DONE] **Step 2: Create `docs/supase-realtime-troubleshooting.md`.**
    * Define the problem: Supabase Realtime broadcast error (`42883`) preventing `fetch_pending.py` from processing comments.
    * Detail the error source: Trigger `realtime_broadcast_comentarios` on `comentarios` table attempting to call `realtime.broadcast_changes()`.
    * List investigation steps:
        - Confirmation of `realtime.broadcast_changes()` existence.
        - Analysis of function signature (`void`) vs. trigger expectation.
        - Attempts to reconfigure trigger and publication.
        - Confirming `comentarios` table is in `supabase_realtime` publication.
    * Summarize current state: Incompatible function signature is the most likely cause.
    * Outline next steps for resolution (e.g., detailed signature analysis, trigger adaptation).

- [DONE] **Step 3: Commit.**

```bash
git add STATE.md docs/supase-realtime-troubleshooting.md
git commit -m "docs: Document Supabase Realtime broadcast error and investigation steps"
```

### Task 2: Investigar Assinatura da Função `realtime.broadcast_changes()`

**Files:**
- Modify: `sql/get_function_signature.sql` (initially for `pg_get_function_arguments`, then updated for `pg_proc` inspection)
- Create: `sql/inspect_realtime_function.sql` (for direct catalog query)

- [DONE] **Step 1: Create a temporary SQL file `sql/get_function_signature.sql` to fetch function signature.**
    * Content: `SELECT pg_get_function_arguments('realtime.broadcast_changes()');`

- [DONE] **Step 2: Execute the SQL query to get the function signature.**
    * Command: `npx supabase db query --linked --file "sql/get_function_signature.sql"`
    * Expected Output: The arguments accepted by the function.
    * **Result:** Failed with `invalid input syntax for type oid`.

- [DONE] **Step 3: Update SQL file to try `pg_get_function_arguments('realtime.broadcast_changes')` format.**
    * Content: `SELECT pg_get_function_arguments('realtime.broadcast_changes');`
    * **Result:** Failed again with `invalid input syntax for type oid`.

- [DONE] **Step 4: Create `sql/inspect_realtime_function.sql` to query `pg_proc` and `pg_namespace` directly.**
    * Content:
```sql
SELECT
    p.proname AS function_name,
    n.nspname AS schema_name,
    pg_get_function_identity_arguments(p.oid) AS identity_arguments,
    pg_get_function_arguments(p.oid) AS arguments,
    p.prorettype::regtype AS return_type
FROM
    pg_catalog.pg_proc p
JOIN
    pg_catalog.pg_namespace n ON n.oid = p.pronamespace
WHERE
    p.proname = 'broadcast_changes' AND n.nspname = 'realtime';
```

- [DONE] **Step 5: Execute the SQL query to inspect the function.**
    * Command: `npx supabase db query --linked --file "sql/inspect_realtime_function.sql"`
    * **Result:** Success!

- [DONE] **Step 6: Analyze the output to confirm the exact signature and expected parameters.**
    * **Function Signature Found:**
        - Schema: `realtime`
        - Function Name: `broadcast_changes`
        - Identity Arguments: `topic_name text, event_name text, operation text, table_name text, table_schema text, new record, old record, level text`
        - Arguments: `topic_name text, event_name text, operation text, table_name text, table_schema text, new record, old record, level text DEFAULT 'ROW'::text`
        - Return Type: `void`
    * This confirms the function exists and accepts specific arguments, contradicting the initial `42883` error. The original trigger call was likely incorrect.

- [DONE] **Step 7: Commit findings.**
    * Committed updated SQL file and plan with findings.

### Task 2.5: Investigate Frontend Issue (Timeline/KPIs Not Opening)

**Files:**
- Read: `src/**/*.js` (focus on files related to KPIs and dashboard)
- Read: `public/**/*.html` (templates related to dashboard/reports)
- Read: `services/dataService.js` (for data fetching)

- [IN PROGRESS] **Step 1: Search for "timeline" and "kpi" in all JS/TS files within `src/` and `public/`.**
    * **Result:** Found references to "kpi", "dashboard", "workers" in `src/core/app.js` (though file access failed), `src/core/state.js`, `src/core/workersUI.js`, and `src/services/dataService.js`. No direct "timeline" references found. References to "dashboard" found in `public/` HTML templates.
    * **Conclusion:** KPIs are likely rendered by JS in `src/` (e.g., `core/app.js`) interacting with data from `services/dataService.js`. Timeline might be part of the dashboard or dynamically loaded.

- [IN PROGRESS] **Step 2: Attempt to read `core/app.js` and `services/dataService.js`.**
    * **Result:** Failed to read both files directly due to "File not found" errors, despite `grep_search` indicating their presence and content. This suggests potential path resolution issues or file access problems.

- [IN PROGRESS] **Step 3: Infer problem based on available information.**
    * **Problem Summary:** Cannot directly access `core/app.js` or `services/dataService.js` for detailed code analysis. However, search results suggest KPIs are managed via JS (likely `core/app.js` or similar) and data fetched via `services/dataService.js` (e.g., `/workers/dashboard` endpoint). Timeline might be part of the dashboard or dynamically loaded.
    * **Likely Causes:**
        1.  **Data Fetching:** Data for KPIs/timeline not retrieved (e.g., `services/dataService.js` issue or backend endpoint problem).
        2.  **Rendering Logic:** JS code in `core/app.js` (or similar) failing to execute or populate elements.
        3.  **HTML Structure:** Missing JS hooks or incorrect linking in `public/` HTML templates.

- [ ] **Step 4: Commit findings and current status of frontend investigation.**
    * Add a note to `docs/supase-realtime-troubleshooting.md` or a new file detailing this frontend investigation and the file access limitations.

### Task 3: Modularize Supabase Interaction in `core/db.py`

**Files:**
- Modify: `core/db.py`
- Create: `core/supabase_service.py` (for specific Supabase operations)

- [ ] **Step 1: Analyze `core/db.py` for existing Supabase-related logic.**
    * Identify functions that directly interact with Supabase (e.g., making queries, managing connections, handling Realtime subscriptions).

- [ ] **Step 2: Create `core/supabase_service.py`.**
    * Define classes or functions for core Supabase operations, such as:
        - Establishing connection/client.
        - Executing raw SQL queries.
        - Managing Realtime subscriptions (if applicable and separate from broadcast).
        - Handling publication/trigger management (potentially a new module if complex).

- [ ] **Step 3: Refactor logic from `core/db.py` to `core/supabase_service.py`.**
    * Move relevant functions and classes, ensuring clear separation of concerns.
    * Update `core/db.py` to import and use the new service.

- [ ] **Step 4: Add docstrings to `core/supabase_service.py`.**
    * Explain the purpose of each class/function and its parameters/return values.

- [ ] **Step 5: Write unit tests for `core/supabase_service.py`.**
    * Focus on testing the core functionality of Supabase interactions.

- [ ] **Step 6: Commit.**

```bash
git add core/db.py core/supabase_service.py tests/core/test_supabase_service.py
git commit -m "refactor: Modularize Supabase interactions into supabase_service.py"
```

### Task 4: Refactor `fetch_pending.py` for Improved Error Handling and Supabase Interaction

**Files:**
- Modify: `fetch_pending.py`
- Read: `core/supabase_service.py` (to use the new modularized functions)

- [ ] **Step 1: Analyze `fetch_pending.py` for its Supabase interaction logic.**
    * Identify how it currently interacts with Supabase, especially for comment updates.

- [ ] **Step 2: Update `fetch_pending.py` to use `core/supabase_service.py`.**
    * Replace direct Supabase calls with calls to the new service layer.

- [ ] **Step 3: Enhance error handling for Supabase operations within `fetch_pending.py`.**
    * Specifically, implement robust handling for Realtime broadcast errors and other potential Supabase API errors.
    * Log errors effectively, referencing the detailed documentation created in Task 1.

- [ ] **Step 4: Add/Update docstrings and comments in `fetch_pending.py`.**
    * Clarify the script's purpose, its interactions with Supabase, and its error handling mechanisms.

- [ ] **Step 5: Write unit tests for the modified `fetch_pending.py`.**
    * Focus on testing error scenarios and successful processing paths.

- [ ] **Step 6: Commit.**

```bash
git add fetch_pending.py core/supabase_service.py tests/test_fetch_pending.py
git commit -m "refactor: Enhance fetch_pending.py with modular Supabase calls and error handling"
```

### Task 5: Revisit Supabase Realtime Trigger/Function Configuration

**Files:**
- Modify: `sql/fix_realtime_trigger.sql` (new file for SQL commands)
- Execute: `npx supabase db query --linked --file "sql/fix_realtime_trigger.sql"`

- [ ] **Step 1: Based on Task 2's findings, create `sql/fix_realtime_trigger.sql`.**
    * This script will attempt to fix the `realtime_broadcast_comentarios` trigger or its associated function.
    * **Hypothesis:** If `realtime.broadcast_changes()` expects no arguments, the trigger might need to be redefined to call it without arguments, or a new function might need to be created that wraps `realtime.broadcast_changes()` with the correct argument passing.
    * **Action:** Attempt to drop and recreate the trigger with the correct function call, or modify the existing one if possible. (Exact SQL depends on Task 2 findings).

- [ ] **Step 2: Execute the SQL script to apply the fix.**
    * Command: `npx supabase db query --linked --file "sql/fix_realtime_trigger.sql"`

- [ ] **Step 3: Verify the fix by running `fetch_pending.py`.**
    * Command: `python fetch_pending.py`
    * Expected Output: Successful processing of comments without Supabase Realtime errors.

- [ ] **Step 4: If successful, update `docs/supase-realtime-troubleshooting.md` with the resolution.**
    * Detail the exact SQL commands used and why they worked.

- [ ] **Step 5: Commit.**

```bash
git add sql/fix_realtime_trigger.sql docs/supase-realtime-troubleshooting.md
git commit -m "fix: Resolve Supabase Realtime broadcast error by reconfiguring trigger/function"
```