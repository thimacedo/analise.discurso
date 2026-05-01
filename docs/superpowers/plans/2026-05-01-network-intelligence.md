# Network Intelligence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Network Intelligence module with three views (Clusters, Timeline, Heatmap) to identify coordinated attack groups.

**Architecture:** 
- **Backend:** New `/api/v1/networks` endpoint in `api/index.py` that calculates connections between authors and targets based on shared metadata and timing.
- **Frontend:** State updates in `state.js` and three new render functions in `ui.js` using D3.js and Vanilla JS.
- **Navigation:** Expandable sidebar menu for selecting views.

**Tech Stack:** FastAPI, Supabase, D3.js (v7), Vanilla JS.

---

### Task 1: Backend API Endpoint `/networks`

**Files:**
- Modify: `api/index.py`
- Test: `tools/test_networks_api.py`

- [ ] **Step 1: Write the failing test**

```python
import httpx
import asyncio

async def test_networks():
    async with httpx.AsyncClient() as client:
        r = await client.get("http://localhost:8000/api/v1/networks")
        assert r.status_code == 200
        data = r.json()
        assert "nodes" in data
        assert "links" in data

if __name__ == "__main__":
    asyncio.run(test_networks())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python tools/test_networks_api.py` (assuming server is not running or route 404s)

- [ ] **Step 3: Implement minimal backend logic**

```python
@app.get("/api/v1/networks")
def get_networks(days: int = 7):
    try:
        supa = get_supa()
        if not supa: return {"nodes": [], "links": []}
        
        # Get hate comments from recent days
        res = supa.table('comentarios').select('autor_username, candidato_id, data_publicacao').eq('is_hate', True).limit(1000).execute()
        data = res.data if res and res.data else []
        
        nodes = {}
        links = []
        
        for item in data:
            author = item.get('autor_username')
            target = item.get('candidato_id')
            if not author or not target: continue
            
            if author not in nodes: nodes[author] = {"id": author, "type": "author", "val": 1}
            else: nodes[author]["val"] += 1
            
            if target not in nodes: nodes[target] = {"id": target, "type": "target", "val": 1}
            
            links.append({"source": author, "target": target, "weight": 1})
            
        return {
            "nodes": list(nodes.values()),
            "links": links[:500] # Limit for performance
        }
    except Exception as e:
        return {"error": str(e)}
```

- [ ] **Step 4: Run test to verify it passes**

- [ ] **Step 5: Commit**

```bash
git add api/index.py
git commit -m "feat(api): add initial /networks endpoint"
```

---

### Task 2: Frontend State & Navigation

**Files:**
- Modify: `src/core/state.js`
- Modify: `index.html`
- Modify: `src/core/ui.js`

- [ ] **Step 1: Add network state**

Modify `src/core/state.js`:
```javascript
export const state = {
    // ... existing
    networkView: 'clusters',
    networkData: { nodes: [], links: [] },
    // ...
}
```

- [ ] **Step 2: Update Sidebar to Sub-menu**

Modify `index.html`:
Replace `<a href="#networks" ...>` with:
```html
<div class="nav-group">
    <a href="#networks" class="nav-item" id="nav-networks">
        <i data-lucide="share-2" class="w-4 h-4"></i> Inteligência de Redes
    </a>
    <div id="sub-networks" class="sub-nav" style="display: none; padding-left: 32px; font-size: 0.8rem; gap: 8px;">
        <a href="#networks/clusters" class="sub-nav-item" onclick="setNetworkView('clusters')">Cluster de Ataque</a>
        <a href="#networks/flow" class="sub-nav-item" onclick="setNetworkView('flow')">Fluxo Coordenado</a>
        <a href="#networks/matrix" class="sub-nav-item" onclick="setNetworkView('matrix')">Matriz de Colusão</a>
    </div>
</div>
```

- [ ] **Step 3: Implement state setters**

Modify `src/core/state.js`:
```javascript
export function setNetworkView(view) {
    state.networkView = view;
    if (window.debouncedRender) window.debouncedRender();
}
```

- [ ] **Step 4: Commit**

```bash
git add src/core/state.js index.html
git commit -m "feat(ui): implement network sub-menu and state"
```

---

### Task 3: Attack Clusters (D3 Graph)

**Files:**
- Modify: `index.html` (add D3)
- Modify: `src/core/ui.js`

- [ ] **Step 1: Add D3.js CDN**

Modify `index.html`:
```html
<script src="https://d3js.org/d3.v7.min.js"></script>
```

- [ ] **Step 2: Implement renderClusters**

Modify `src/core/ui.js`:
```javascript
function renderClusters() {
    const container = document.getElementById('view-networks');
    container.innerHTML = '<canvas id="network-canvas" style="width:100%; height:600px"></canvas>';
    const canvas = document.getElementById('network-canvas');
    // D3 Force implementation on Canvas...
}
```

- [ ] **Step 3: Commit**

```bash
git add index.html src/core/ui.js
git commit -m "feat(ui): implement cluster graph visualization"
```

---

### Task 4: Coordinated Flow (Timeline)

**Files:**
- Modify: `src/core/ui.js`

- [ ] **Step 1: Implement renderFlow**

Modify `src/core/ui.js`:
```javascript
function renderFlow() {
    const container = document.getElementById('view-networks');
    container.innerHTML = `<h3>Fluxo Coordenado</h3><div id="flow-timeline"></div>`;
    // Timeline logic...
}
```

- [ ] **Step 2: Commit**

```bash
git add src/core/ui.js
git commit -m "feat(ui): implement coordinated flow timeline"
```

---

### Task 5: Collusion Matrix (Heatmap)

**Files:**
- Modify: `src/core/ui.js`

- [ ] **Step 1: Implement renderMatrix**

Modify `src/core/ui.js`:
```javascript
function renderMatrix() {
    const container = document.getElementById('view-networks');
    container.innerHTML = `<h3>Matriz de Colusão</h3><div id="collusion-heatmap"></div>`;
    // Heatmap logic...
}
```

- [ ] **Step 2: Commit**

```bash
git add src/core/ui.js
git commit -m "feat(ui): implement collusion matrix heatmap"
```
