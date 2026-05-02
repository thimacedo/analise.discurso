# TASK: Refatoração Estética e de Layout - Sentinela Democrática v20.1

Este documento contém o código-fonte integral dos arquivos de frontend para que um Agente de Frontend realize o tratamento visual, ajuste de densidade e correção de layout (scroll independente e tamanhos de fonte).

## Contexto do Projeto
- **Objetivo**: Dashboard forense para monitoramento de discurso de ódio.
- **Tecnologias**: HTML5, Vanilla CSS, Vanilla JS (ES Modules), TailwindCSS (utilizado pontualmente), D3.js (gráficos), Lucide Icons.
- **Pain Point**: O layout atual possui fontes desproporcionalmente grandes e uma coluna de "Análise de Risco" que gera scroll infinito na página, em vez de ter scroll interno.

---

## 1. index.html
O esqueleto do dashboard. Contém a estrutura de `aside` (sidebar) e `main`.

```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SENTINELA | Diamond Edition v20.1.0</title>
    <link rel="icon" type="image/png" href="/favicon.png">
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <link rel="stylesheet" href="/src/styles/main.css?v=20.1.0">
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <script>
        window.SENTINELA_CONFIG = {
            apiUrl: '/api/v1',
            supabaseUrl: 'https://vhamejkldzxbeibqeqpk.supabase.co',
            supabaseKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZoYW1lamtsZHp4YmVpYnFlcXBrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjQ4ODEyNSwiZXhwIjoyMDkyMDY0MTI1fQ.GfvAI7rV8isgdhVeJp4mOUscWpdOqOuBoURGm82VdtY',
            refreshInterval: 3600000 
        };
    </script>
</head>
<body class="custom-scrollbar">
    <aside>
        <div class="brand-block">
            <div class="brand-mark"><img src="/logo_transparente.png" alt="Logo Sentinela"></div>
            <div>
                <h1>Sentinela</h1>
                <span>Diamond v20.1.0</span>
                <div class="stn-counter glass-card" style="margin-top: 10px; display: flex; align-items: center; gap: 8px; padding: 4px 12px; border-color: var(--accent); background: rgba(220, 38, 38, 0.05);">
                    <i data-lucide="zap" style="width: 14px; height: 14px; color: var(--accent);"></i>
                    <span id="stn-balance" class="stn-text">-- STN</span>
                </div>
            </div>
        </div>

        <nav class="side-nav">
            <a href="#monitor" class="nav-item active" id="nav-monitor"><i data-lucide="layout-grid" class="w-4 h-4"></i> Panorama Global</a>
            
            <div class="nav-group">
                <a href="#networks" class="nav-item" id="nav-networks" onclick="document.getElementById('sub-networks').style.display='flex'">
                    <i data-lucide="share-2" class="w-4 h-4"></i> Inteligência de Redes
                </a>
                <div id="sub-networks" class="sub-nav" style="display: none; flex-direction: column; padding-left: 32px; font-size: 0.75rem; gap: 8px; margin-top: 4px; margin-bottom: 8px;">
                    <a href="#networks" onclick="window.setNetworkView('clusters')" class="sub-nav-link" id="nav-net-clusters" style="color: var(--text-muted); text-decoration: none;">• Cluster de Ataque</a>
                    <a href="#networks" onclick="window.setNetworkView('flow')" class="sub-nav-link" id="nav-net-flow" style="color: var(--text-muted); text-decoration: none;">• Fluxo Coordenado</a>
                    <a href="#networks" onclick="window.setNetworkView('matrix')" class="sub-nav-link" id="nav-net-matrix" style="color: var(--text-muted); text-decoration: none;">• Matriz de Colusão</a>
                </div>
            </div>

            <a href="#directory" class="nav-item" id="nav-directory"><i data-lucide="users" class="w-4 h-4"></i> Perfis Monitorados</a>
            <a href="#dossie" class="nav-item" id="nav-dossie"><i data-lucide="fingerprint" class="w-4 h-4"></i> Dossiê de Alvos</a>
            <a href="#map" class="nav-item" id="nav-map"><i data-lucide="globe" class="w-4 h-4"></i> Geopolítica UF</a>
        </nav>

        <div class="sidebar-footer glass-card">
            <span id="status-sync" class="status-copy">Conectado ao Proxy...</span>
            <button type="button" class="ghost-btn sync-btn" onclick="window.forceRefresh()">Sincronizar Dados</button>
        </div>
    </aside>

    <main class="custom-scrollbar">
        <header class="main-header">
             <div id="active-filter"></div>
             <div class="status-chip is-ok">Sinal Operacional</div>
        </header>

        <header class="kpi-grid">
            <div class="glass-card metric-card"><span class="kpi-label">Monitorados</span><div id="kpi-monitorados" class="kpi-value">---</div></div>
            <div class="glass-card metric-card metric-card--danger"><span class="kpi-label">Alertas PASA</span><div id="kpi-hate" class="kpi-value">---</div></div>
            <div class="glass-card metric-card"><span class="kpi-label">Amostragem</span><div id="kpi-total" class="kpi-value">---</div></div>
            <div class="glass-card metric-card metric-card--success"><span class="kpi-label">Resiliência</span><div id="kpi-res" class="kpi-value">---</div></div>
        </header>

        <div class="dashboard-toolbar glass-card">
            <div class="filter-group">
                <span class="eyebrow filter-label">Filtros:</span>
                <button onclick="window.setDashboardFilter('all')" id="btn-filter-all" class="filter-chip active">Todos</button>
                <button onclick="window.setDashboardFilter('hate')" id="btn-filter-hate" class="filter-chip">Com Alertas</button>
                <button onclick="window.setDashboardFilter('critical')" id="btn-filter-critical" class="filter-chip">Risco Crítico</button>
            </div>
            <div class="search-box">
                <i data-lucide="search" class="search-icon"></i>
                <input type="text" placeholder="Buscar alvo ou estado..." oninput="window.setDashboardSearch(this.value)" class="search-input">
            </div>
        </div>

        <section id="view-monitor" class="view-content" style="display: flex;">
            <div class="monitor-grid">
                <div class="monitor-side" style="display: flex; flex-direction: column; gap: 16px;">
                    <div class="glass-card section-card">
                        <div class="section-heading"><div><span class="eyebrow">Linha do Tempo</span><h3>Evidências PASA</h3></div></div>
                        <div id="feed-alertas" class="stack-list" style="max-height: 800px; overflow-y: auto;"></div>
                    </div>
                </div>
                <div class="glass-card section-card">
                    <div class="section-heading"><div><span class="eyebrow">Análise de Risco</span><h3>Prioridade de Triagem</h3></div></div>
                    <div id="chartMain" class="stack-list"></div>
                </div>
            </div>
            
            <div class="glass-card section-card" style="margin-top: 20px;">
                <div class="section-heading"><div><span class="eyebrow">Monitoramento Estutural</span><h3>Evolução das Categorias PASA</h3></div></div>
                <div id="pasa-temporal-chart" style="width: 100%; min-height: 350px;"></div>
            </div>
        </section>

        <section id="view-networks" class="view-content" style="display: none;"></section>
        <section id="view-directory" class="view-content" style="display: none;"></section>
        <section id="view-dossie" class="view-content" style="display: none;"></section>
        <section id="view-map" class="view-content" style="display: none;"></section>
    </main>

    <script type="module" src="/src/core/app.js?v=20.1.0"></script>
    <script type="module" src="/src/core/payments.js?v=20.1.0"></script>
</body>
</html>
```

---

## 2. src/styles/main.css
O arquivo de estilos. Foco em `.kpi-value`, `.monitor-grid`, `.monitor-row` e regras de tipografia.

```css
:root {
    --bg-base: #020617;
    --bg-panel: rgba(15, 23, 42, 0.7);
    --bg-soft: rgba(148, 163, 184, 0.08);
    --border: rgba(6, 182, 212, 0.15);
    --border-bright: rgba(6, 182, 212, 0.4);
    --text-main: #f8fafc;
    --text-soft: #cbd5e1;
    --text-muted: #64748b;
    --accent: #06b6d4;
    --accent-strong: #0891b2;
    --diamond-shine: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 50%, rgba(255,255,255,0.05) 100%);
    --danger: #ef4444;
    --success: #10b981;
    --warn: #f59e0b;
    --font-mono: 'JetBrains Mono', monospace;
    --font-sans: 'Plus Jakarta Sans', sans-serif;
    --glow-subtle: 0 0 15px rgba(6, 182, 212, 0.1);
    --glow-strong: 0 0 30px rgba(6, 182, 212, 0.2);
    --glass-blur: blur(12px);
}

body {
    min-height: 100vh;
    width: 100%;
    background: radial-gradient(circle at 10% 20%, rgba(6, 182, 212, 0.05), transparent 40%), var(--bg-base);
    color: var(--text-main);
    font-family: var(--font-sans);
    display: flex;
    overflow-y: auto;
}

.kpi-value {
    margin-top: 8px;
    font-size: clamp(1.2rem, 1.8vw, 1.8rem);
    font-weight: 800;
    font-family: var(--font-mono);
    letter-spacing: -0.05em;
    background: linear-gradient(180deg, #fff 0%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.monitor-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.6fr) minmax(320px, 0.95fr);
    gap: 20px;
    align-items: start;
    max-height: calc(100vh - 250px);
}

.stack-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow-y: auto;
}

#feed-alertas, #chartMain {
    max-height: calc(100vh - 320px) !important;
}

.monitor-row {
    width: 100%;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.03);
    padding: 10px 14px;
    text-align: left;
    cursor: pointer;
}

.profile-avatar {
    width: 60px;
    height: 60px;
    font-size: 1.4rem;
    font-weight: 800;
}

.post-content {
    font-size: 0.85rem;
    line-height: 1.4;
    padding: 10px;
}
/* ... restante omitido para brevidade no exemplo, mas disponível no arquivo real ... */
```

---

## 3. src/core/ui.js
A lógica de renderização do DOM. Foco na função `renderAlertasFeed` e `renderMonitorImpacto`.

```javascript
/* Conteúdo integral lido anteriormente */
import { state, ... } from './state.js';

export function renderAll() { ... }

function renderAlertasFeed() {
    // Renderiza os cards de alerta. Substituir "INFO" pela plataforma.
    const html = list.map((alerta) => {
        const plataforma = (alerta.plataforma || 'instagram').toLowerCase();
        // ... (lógica de ícones)
        return `
            <article class="alert-post-card">
                <div class="post-header">
                    <span class="cat-badge">${plataforma.toUpperCase()}</span>
                    <span class="severity-pill">${alerta.severidade || 'ALERTA'}</span>
                </div>
                <div class="post-content">"${alerta.texto_bruto}"</div>
            </article>
        `;
    });
}
```

---

## 4. src/core/app.js & state.js
Inicialização e estado.

```javascript
// app.js
async function init() {
    await authService.init();
    await refreshData();
}

// state.js
export const state = {
    view: 'monitor',
    selectedAlvo: null,
    alertas: [],
    // ...
};
```
