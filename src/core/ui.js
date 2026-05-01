import { state, setDossieGrouping, setDossieSearch, setViewState, setNetworkView } from './state.js';
import { renderBrazilMap } from '../components/BrazilMap.js';
import { planService } from '../services/dataService.js';
import { authService } from '../services/authService.js';

export function renderAll() {
    try {
        updateSidebarActive();
        renderKPIs();
        renderTopbar();
        renderSTN();

        const views = ['monitor', 'networks', 'dossie', 'map', 'directory'];
        views.forEach((view) => {
            const el = document.getElementById(`view-${view}`);
            if (el) el.style.display = state.view === view ? 'flex' : 'none';
        });

        // Toggle sub-menu visibility
        const subNav = document.getElementById('sub-networks');
        if (subNav) subNav.style.display = (state.view === 'networks') ? 'flex' : 'none';

        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderAlertasFeed();
        } else if (state.view === 'networks') {
            renderNetworkIntelligence();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        } else if (state.view === 'map') {
            renderGeopolitica();
        } else if (state.view === 'directory') {
            renderDirectory();
        }

        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error('Render error:', e);
    }
}

function updateSidebarActive() {
    document.querySelectorAll('.nav-item').forEach((nav) => {
        const href = nav.getAttribute('href').substring(1);
        nav.classList.toggle('active', state.view === href || (state.view.startsWith('networks') && href === 'networks'));
    });
}

function renderKPIs() {
    if (!state.summary) return;
    const target = state.selectedAlvo;
    const isFiltered = !!target;
    const set = (id, value, trend = 0, label = null) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (label) {
            const labelEl = el.previousElementSibling;
            if (labelEl && labelEl.classList.contains('kpi-label')) labelEl.innerText = label;
        }
        el.innerHTML = `
            <div class="kpi-value animate-in">${value}</div>
            <div class="kpi-trend ${trend > 0 ? 'up' : trend < 0 ? 'down' : 'neutral'}">
                <i data-lucide="${trend > 0 ? 'trending-up' : trend < 0 ? 'trending-down' : 'minus'}" style="width:12px;height:12px"></i>
                ${trend !== 0 ? Math.abs(trend) + '%' : 'Estável'}
            </div>
        `;
    };
    const s = state.summary;
    const t = s.trends || { hate_trend_pct: 0, resiliencia_trend_pct: 0 };
    if (isFiltered) {
        const total = target.comentarios_totales_count || 0;
        const hate = target.comentarios_odio_count || 0;
        const res = total > 0 ? (((total - hate) / total) * 100).toFixed(1) : '100.0';
        set('kpi-monitorados', '@' + target.username, 0, 'Foco Atual');
        set('kpi-hate', hate.toLocaleString(), 0, 'Alertas do Alvo');
        set('kpi-total', formatCompactNumber(total), 0, 'Amostra do Alvo');
        set('kpi-res', `${res}%`, 0, 'Resiliência Indiv.');
    } else {
        set('kpi-monitorados', s.total_monitorados.toLocaleString(), 0, 'Monitorados');
        set('kpi-hate', s.total_alertas.toLocaleString(), t.hate_trend_pct, 'Alertas PASA');
        set('kpi-total', formatCompactNumber(s.total_amostra), 0, 'Amostragem');
        set('kpi-res', `${s.resiliencia}%`, t.resiliencia_trend_pct, 'Resiliência');
    }
}

function formatCompactNumber(number) {
    if (number < 1000) return number;
    if (number < 1000000) return (number / 1000).toFixed(1) + 'K';
    return (number / 1000000).toFixed(1) + 'M';
}

function renderTopbar() {
    const syncEl = document.getElementById('status-sync');
    const filterEl = document.getElementById('active-filter');
    if (syncEl) syncEl.innerText = state.lastSyncAt ? `Sincronizado: ${new Date(state.lastSyncAt).toLocaleTimeString('pt-BR')}` : 'Aguardando leitura...';
    if (filterEl) {
        if (state.selectedAlvo) {
            filterEl.innerHTML = `<div class="filter-pill" style="background: rgba(37, 99, 235, 0.2); padding: 4px 12px; border-radius: 20px; font-size: 11px; display: flex; align-items: center; gap: 8px; border: 1px solid rgba(37, 99, 235, 0.4);"><i data-lucide="crosshair" class="w-3 h-3"></i> Foco: @${state.selectedAlvo.username} <button type="button" onclick="window.setFiltroAlvo(null)" style="background: none; border: 0; color: white; cursor: pointer;"><i data-lucide="x" class="w-3 h-3"></i></button></div>`;
        } else {
            filterEl.innerHTML = '';
        }
    }
}

function renderAlertasFeed() {
    const container = document.getElementById('feed-alertas');
    if (!container) return;
    if (state.loading) { container.innerHTML = createEmptyState('loader', 'Atualizando alertas', 'Sincronizando com o banco...'); return; }
    if (!planService.canAccess('alerts')) { container.innerHTML = createUpgradeGate('Acesso Pro Necessário', 'O feed de alertas ativos é exclusivo para assinantes.'); return; }
    const list = state.selectedAlvo ? state.alertas.filter((alerta) => String(alerta.candidato_id) === String(state.selectedAlvo.username)) : state.alertas;
    if (!list.length) { container.innerHTML = createEmptyState('shield-check', 'Nenhum alerta ativo', 'Sem sinais críticos para este filtro.'); return; }
    container.innerHTML = list.map((alerta) => {
        const severity = alerta.severidade || 'INFO';
        const agressor = alerta.autor_username || 'anônimo';
        const target = alerta.candidato_id || 'alvo';
        const plataforma = (alerta.plataforma || 'instagram').toLowerCase();
        const platIcon = plataforma === 'youtube' ? 'youtube' : 'instagram';
        const platColor = plataforma === 'youtube' ? '#ff0000' : '#e1306c';
        return `
            <article class="alert-card border-${severity.toLowerCase()}">
                <div class="alert-card__header">
                    <div>
                        <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px">
                            <i data-lucide="${platIcon}" style="width:12px; height:12px; color:${platColor}"></i>
                            <span class="eyebrow" style="color:var(--danger); margin:0">Agressor: @${agressor}</span>
                        </div>
                        <h4>➔ contra @${target}</h4>
                    </div>
                    <div style="display:flex; align-items:center; gap:10px">
                        <span class="severity-pill is-${severity.toLowerCase()}">${severity}</span>
                        <button onclick="window.toggleTriage('${alerta.id}')" class="ghost-btn" style="padding:4px"><i data-lucide="more-horizontal" class="w-4 h-4"></i></button>
                    </div>
                </div>
                <div id="triage-actions-${alerta.id}" style="display:none; gap:8px; margin-bottom:12px; padding:10px; background:rgba(0,0,0,0.2); border-radius:8px">
                    <button onclick="window.markFalsePositive('${alerta.id}')" class="filter-chip" style="background:var(--success); color:white; border:none">Marcar Falso Positivo (Limpar)</button>
                </div>
                <p>"${alerta.texto_bruto || alerta.descricao || 'Sem conteúdo'}"</p>
                <div class="alert-card__meta">
                    <span>${formatCategory(alerta.categoria_ia || 'HOSPITALIDADE')}</span>
                    <span>${new Date(alerta.data_coleta || alerta.created_at || Date.now()).toLocaleString('pt-BR')}</span>
                </div>
            </article>
        `;
    }).join('');
}

function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if (!container) return;
    if (state.loading) { container.innerHTML = createEmptyState('loader', 'Compilando...', ''); return; }
    let list = [...state.data];
    if (state.filterHateOnly === 'hate') list = list.filter(a => a.comentarios_odio_count > 0);
    else if (state.filterHateOnly === 'critical') list = list.filter(a => a.score_risco > 80);
    if (state.dashboardSearch) {
        const q = state.dashboardSearch.toLowerCase();
        list = list.filter(a => a.username.toLowerCase().includes(q) || (a.estado && a.estado.toLowerCase().includes(q)));
    }
    document.querySelectorAll('.filter-chip').forEach(chip => {
        const type = chip.id.replace('btn-filter-', '');
        chip.classList.toggle('active', (state.filterHateOnly || 'all') === type);
    });
    if (list.length === 0) { container.innerHTML = createEmptyState('search-x', 'Nenhum alvo corresponde ao filtro', ''); return; }
    const PASA_ICONS = {"ODIO_IDENTITARIO": "users", "VIOLENCIA_GENERO": "shield-alert", "AMEACA": "alert-octagon", "INSULTO_AD_HOMINEM": "swords", "ATAQUE_INSTITUCIONAL": "landmark", "RIGOR_CRIMINAL": "scale"};
    container.innerHTML = list.map((alvo, index) => {
        const ratio = alvo.comentarios_totales_count > 0 ? ((alvo.comentarios_odio_count / alvo.comentarios_totales_count) * 100).toFixed(1) : '0.0';
        const isActive = state.selectedAlvo && state.selectedAlvo.username === alvo.username;
        const breakdown = alvo.breakdown || {};
        const badgesHtml = Object.entries(breakdown).map(([cat, count]) => `<span class="cat-badge ${count > 0 ? 'has-count is-hate' : ''}" title="${cat}"><i data-lucide="${PASA_ICONS[cat] || 'help-circle'}"></i> ${count}</span>`).join('');
        return `
            <button type="button" onclick="window.setFiltroAlvo('${alvo.username}')" class="monitor-row ${isActive ? 'is-active' : ''}">
                <div class="monitor-row__title"><div><span class="eyebrow">${alvo.estado || 'BR'} • Prioridade ${index + 1}</span><strong>@${alvo.username}</strong></div><span style="color:${alvo.color}">${alvo.comentarios_odio_count} alertas</span></div>
                <div class="monitor-row__details">${badgesHtml || '<span class="cat-badge">Sem evidências</span>'}</div>
                <div class="progress-track"><div class="progress-bar" style="width:${alvo.score_risco}%; background:${alvo.color || 'var(--danger)'}"></div></div>
                <div class="monitor-row__meta"><span>Risco: ${alvo.score_risco}%</span><span>${ratio}% toxicidade</span></div>
            </button>
        `;
    }).join('');
}

function renderNetworkIntelligence() {
    const container = document.getElementById('view-networks');
    if (!container) return;
    if (!planService.canAccess('networks')) { container.innerHTML = createUpgradeGate('Inteligência de Redes', 'Exclusivo Enterprise.'); return; }
    document.querySelectorAll('.sub-nav-link').forEach(link => {
        const isCurrent = link.id === `nav-net-${state.networkView}`;
        link.style.color = isCurrent ? 'var(--accent)' : 'var(--text-muted)';
        link.style.fontWeight = isCurrent ? '800' : 'normal';
    });
    if (state.networkView === 'clusters') renderClusters(container);
    else if (state.networkView === 'flow') renderFlow(container);
    else if (state.networkView === 'matrix') renderMatrix(container);
}

function renderClusters(container) {
    container.innerHTML = `<div class="section-heading"><div><span class="eyebrow">D3-Force</span><h3>Cluster de Ataque</h3></div><div style="display:flex; gap:16px; font-size:11px"><div style="display:flex; align-items:center; gap:6px"><div style="width:10px; height:10px; border-radius:50%; background:#ef4444"></div> Candidato</div><div style="display:flex; align-items:center; gap:6px"><div style="width:10px; height:10px; border-radius:50%; background:#2563eb"></div> Agressor</div></div></div><div class="glass-card" style="width:100%; min-height:600px; position:relative; overflow:hidden; background: #0a0a0c;"><canvas id="network-canvas" style="cursor: grab;"></canvas><div id="hover-info" style="position:absolute; bottom:20px; left:20px; background:rgba(0,0,0,0.8); padding:10px; border-radius:8px; border:1px solid var(--accent); display:none; pointer-events:none;"></div></div>`;
    const canvas = document.getElementById('network-canvas');
    if (!canvas || !state.networks?.nodes?.length) return;
    const ctx = canvas.getContext('2d');
    const width = container.offsetWidth - 40;
    const height = 600;
    canvas.width = width; canvas.height = height;
    const nodes = state.networks.nodes.map(d => ({ ...d }));
    const links = state.networks.links.map(d => ({ ...d }));
    const simulation = d3.forceSimulation(nodes).force("link", d3.forceLink(links).id(d => d.id).distance(80)).force("charge", d3.forceManyBody().strength(-300)).force("center", d3.forceCenter(width / 2, height / 2)).force("collision", d3.forceCollide().radius(30));
    let transform = d3.zoomIdentity;
    d3.select(canvas).call(d3.zoom().scaleExtent([0.2, 5]).on("zoom", (event) => { transform = event.transform; draw(); }));
    function draw() {
        ctx.save(); ctx.clearRect(0, 0, width, height); ctx.translate(transform.x, transform.y); ctx.scale(transform.k, transform.k);
        ctx.beginPath(); ctx.strokeStyle = "rgba(255,255,255,0.08)"; links.forEach(d => { ctx.moveTo(d.source.x, d.source.y); ctx.lineTo(d.target.x, d.target.y); }); ctx.stroke();
        nodes.forEach(d => { ctx.beginPath(); const r = d.type === 'target' ? 12 : 5; ctx.arc(d.x, d.y, r, 0, 2 * Math.PI); ctx.fillStyle = d.type === 'target' ? "#ef4444" : "#2563eb"; ctx.fill(); if (d.type === 'target' || transform.k > 1.2) { ctx.fillStyle = "white"; ctx.font = `${10/transform.k}px Inter`; ctx.textAlign = "center"; ctx.fillText(`@${d.id}`, d.x, d.y + r + 10); } });
        ctx.restore();
    }
    simulation.on("tick", draw);
}

function renderFlow(container) {
    const list = state.selectedAlvo ? state.alertas.filter(a => a.candidato_id === state.selectedAlvo.username) : state.alertas;
    container.innerHTML = `<div class="section-heading"><div><span class="eyebrow">Análise Temporal</span><h3>Fluxo Coordenado</h3></div></div><div class="stack-list glass-card" style="padding:20px"><table style="width:100%; border-collapse:collapse; font-size:0.85rem"><thead><tr style="text-align:left; border-bottom:1px solid rgba(255,255,255,0.1)"><th style="padding:12px">Horário</th><th>Agressor</th><th>Foco</th><th>Plataforma</th></tr></thead><tbody>${list.map(a => `<tr style="border-bottom:1px solid rgba(255,255,255,0.05)"><td style="padding:12px; font-family:monospace; color:var(--text-muted)">${new Date(a.data_coleta).toLocaleTimeString('pt-BR')}</td><td><strong>@${a.autor_username}</strong></td><td style="color:var(--danger)">➔ @${a.candidato_id}</td><td><i data-lucide="${a.plataforma==='youtube'?'youtube':'instagram'}" style="width:14px; height:14px"></i></td></tr>`).join('')}</tbody></table></div>`;
}

function renderMatrix(container) {
    const multiAuthors = state.networks.multi_target_authors || [];
    const targets = [...new Set((state.networks.links || []).map(l => l.target.id || l.target))].slice(0, 15);
    container.innerHTML = `<div class="section-heading"><div><span class="eyebrow">Matriz de Eficácia</span><h3>Agressores Multi-Alvos</h3></div></div><div class="glass-card" style="padding:20px; overflow-x:auto"><div class="matrix-grid" style="display:grid; grid-template-columns: 150px repeat(${targets.length}, 1fr); gap:4px"><div></div>${targets.map(t => `<div style="font-size:9px; transform:rotate(-45deg); height:50px">@${t}</div>`).join('')}${multiAuthors.map(a => `<div style="font-size:11px; font-weight:bold">@${a}</div>${targets.map(t => { const link = state.networks.links.find(l => (l.source.id || l.source) === a && (l.target.id || l.target) === t); return `<div style="background:${link?'rgba(239, 68, 68, 0.4)':'rgba(255,255,255,0.02)'}; height:25px"></div>`; }).join('')}`).join('')}</div></div>`;
}

function renderDirectory() {
    const container = document.getElementById('view-directory');
    if (!container) return;
    const list = state.data || [];
    container.innerHTML = `<div class="section-heading"><div><span class="eyebrow">Repositório</span><h3>Diretório de Perfis Monitorados</h3></div></div><div class="dossie-card-grid">${list.map(item => `
        <div class="dossie-card glass-card">
            <div class="dossie-card__header"><span class="status-chip is-ok">${item.estado || 'BR'}</span><h5>@${item.username}</h5></div>
            <p style="font-size:12px; margin:8px 0">${item.nome_completo || 'Candidato'}</p>
            <div class="dossie-card__stats">
                <div><span>Alertas</span><strong>${item.comentarios_odio_count}</strong></div>
                <div><span>Risco</span><strong>${item.score_risco}%</strong></div>
                <div><span>Status</span><strong style="color:var(--success)">ATIVO</strong></div>
            </div>
            <button class="stn-action-btn stn-btn-active" onclick="window.inspectTarget('${item.username}')">Acessar Panorama</button>
        </div>
    `).join('')}</div>`;
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid-container');
    if (!container) return;
    const list = state.data || [];
    container.innerHTML = list.map(item => `<div class="dossie-card glass-card"><div class="dossie-card__header"><span class="status-chip is-ok">${item.estado || 'BR'}</span><h5>@${item.username}</h5></div><p>${item.nome_completo || 'Candidato'}</p><div class="dossie-card__stats"><div><span>Total</span><strong>${item.comentarios_totales_count}</strong></div><div><span>Ódio</span><strong>${item.comentarios_odio_count}</strong></div><div><span>Risco</span><strong>${item.score_risco}%</strong></div></div><button class="stn-action-btn stn-btn-active" onclick="window.inspectTarget('${item.username}')">Gerar Dossiê Forense</button></div>`).join('');
}

function renderGeopolitica() {
    const container = document.getElementById('view-map');
    if (!container) return;
    container.innerHTML = `<h3>Geopolítica UF</h3><div id="map-container"></div>`;
    renderBrazilMap('map-container', state.geo);
}

function createUpgradeGate(title, description) { return `<div class="upgrade-gate glass-card"><div class="upgrade-gate__icon"><i data-lucide="lock" class="w-8 h-8"></i></div><h3>${title}</h3><p>${description}</p><button class="cta-upgrade" onclick="window.open('/pricing')">Fazer Upgrade →</button></div>`; }
function createEmptyState(icon, title, description) { return `<div class="empty-state"><div class="empty-state__icon"><i data-lucide="${icon}"></i></div><strong>${title}</strong><p>${description}</p></div>`; }
function formatCategory(category) { return String(category).replace(/_/g, ' ').toUpperCase(); }

window.inspectTarget = (username) => {
    const alvo = state.data.find((item) => item.username === username);
    if (alvo) { state.selectedAlvo = alvo; setViewState('monitor'); renderAll(); }
};

window.setFiltroAlvo = (id) => {
    state.selectedAlvo = id ? state.data.find((item) => item.username === id) : null;
    renderAll();
};

window.setViewState = setViewState;
window.setNetworkView = setNetworkView;
window.setDossieGrouping = setDossieGrouping;
window.setDossieSearch = setDossieSearch;

function renderSTN() {
    const el = document.getElementById('stn-balance');
    if (el) { const tokens = authService.user?.stn_tokens || 0; el.innerText = `${tokens} STN`; }
}
