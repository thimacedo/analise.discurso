# Research Report: Frontend Resilience & Memory Optimization (v20.6)

**Status:** Completed
**Date:** 2026-05-09
**Researcher:** Pickle Rick 🥒

## 1. Frontend Failure Analysis (UI Fragility)

### 1.1 Root Cause: Unsafe Property Access
The "White Screen of Death" occurs primarily in `src/core/app.js` and `src/core/ui.js` when API calls fail or return unexpected formats.

- **`src/core/app.js:84`**: `state.summary = summary;` directly assigns the API result. If `summary` is null/undefined, subsequent access to `state.summary.total_monitorados` (Line 100) throws a `TypeError`.
- **`src/core/app.js:158`**: `state.currentPage = 1;` is called after data processing. If the `try...catch` block (Lines 77-170) catches an error, `state.loading` is set to false, but the UI might be in an inconsistent state.
- **`src/core/ui.js:12`**: `alerta?.texto_limpo?.trim();` uses optional chaining, which is good, but the logic in `renderFeed` (Lines 108-140) still depends on `alertas` being an array.

### 1.2 Mitigation Strategy: Null-Safety
- Wrap `renderAll` call in `app.js:163` with strict fallbacks: `renderAll(summary || {}, targets || [], alerts || [])`.
- Implement `EmptyState` component in `ui.js` for when `alertas.length === 0`.

## 2. Memory & Performance Analysis (OOM)

### 2.1 The 7.4GB Crash
The crash report mentioned 7.46 GB of RAM usage.
- **`src/services/dataService.js:80`**: `getTargets` has a default `limit = 50`.
- **`src/core/app.js:80`**: `dataService.getAlerts(20, 1)` was recently optimized to 20, but `getTargets()` still loads 50.
- **`src/core/ui.js:120`**: The `map` function in `renderFeed` creates a massive string of HTML in memory before injecting into `container.innerHTML`. For large datasets, this is extremely expensive.

### 2.2 Optimization Strategy
- **Pagination**: Force `limit = 20` in all initial service calls.
- **DOM Fragment**: Instead of `.map().join('')`, use `document.createDocumentFragment()` or batch injection for `renderFeed`.

## 3. Monetization Failure Analysis

### 3.1 AdSense Error 400
- **`index.html:179`**: `data-ad-slot="SIDEBAR_DIAMOND"` is a placeholder string. AdSense expects a 10-digit numerical ID.
- **`src/core/ui.js:134`**: `data-ad-slot="XXXXXX"` in the dynamic feed injection also uses a placeholder.

### 3.2 Stripe test IDs
- **`src/services/paymentService.js`** (referenced by `payments.js`): Needs investigation to find `price_1Starter` and replace with a variable or production ID.

## 4. Cache Management

- **Current State**: `src/core/app.js` is imported in `index.html` with `?v=20.5.0`.
- **Problem**: Individual modules (like `ui.js`) imported *inside* `app.js` are not versioned, leading to "Partial Updates" where `app.js` is new but `ui.js` is from cache.
- **Solution**: Move to a build step or manually update all internal imports to `?v=20.6.0`.

---
*🥒 "I'm not just a scientist, Morty. I'm a researcher of your failures."*
