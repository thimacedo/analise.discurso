# Workers UI Infrastructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update `index.html` to include the navigation link for "Workers" and its corresponding content section.

**Architecture:** Vanilla HTML/CSS with Lucide Icons for the sidebar navigation and a hidden section in the main view container.

**Tech Stack:** HTML5, Lucide Icons.

---

### Task 1: Update Sidebar Navigation

**Files:**
- Modify: `index.html:62-63`

- [ ] **Step 1: Add "Workers" link to the sidebar**
  Find the `#nav-map` link and add the `#nav-workers` link immediately after it.

```html
            <a href="#map" class="nav-item" id="nav-map"><i data-lucide="globe" class="w-5 h-5"></i> <span>Mapa</span></a>
            <a href="#workers" class="nav-item" id="nav-workers"><i data-lucide="activity" class="w-5 h-5"></i> <span>Workers</span></a>
```

- [ ] **Step 2: Verify Sidebar update**
  Check that the new link exists in `index.html`.

### Task 2: Update Main Content Container

**Files:**
- Modify: `index.html:92-93`

- [ ] **Step 1: Add Workers view section**
  Find the `#view-map` section and add the `#view-workers` section immediately after it.

```html
            <section id="view-map" class="view-content"></section>
            <section id="view-workers" class="view-content"></section>
```

- [ ] **Step 2: Verify Section update**
  Check that the new section exists in `index.html`.

### Task 3: Final Verification and Commit

- [ ] **Step 1: Run a simple grep check to ensure elements are present**
  Run: `grep -E "id=\"nav-workers\"|id=\"view-workers\"" index.html`
  Expected: Both IDs should be present in the output.

- [ ] **Step 2: Commit changes**

```bash
git add index.html
git commit -m "feat(ui): add workers tab and section to index.html"
```
