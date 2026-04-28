import { state, setDossieGrouping, setDossieSearch } from './state.js';
import { renderBrazilMap } from '../components/BrazilMap.js';

export function renderAll() {
    try {
        updateSidebarActive();
        renderKPIs();
        renderTopbar();

        const views = ['monitor', 'networks', 'dossie', 'map'];
        views.forEach((view) => {
            const el = document.getElementById(`view-${view}`);
            if (el) el.style.display = state.view === view ? 'flex' : 'none';
        });

        if (state.view === 'monitor') {
            renderMonitorImpacto();
            renderAlertasFeed();
        } else if (state.view === 'networks') {
            renderNetworkIntelligence();
        } else if (state.view === 'dossie') {
            renderDossieGrid();
        } else if (state.view === 'map') {
            renderGeopolitica();
        }

        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error('Render error:', e);
    }
}

function updateSidebarActive() {
    document.querySelectorAll('.nav-item').forEach((nav) => {
        nav.classList.toggle('active', nav.getAttribute('href') === `#${state.view}`);
    });
}

function renderKPIs() {
    const set = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.innerText = value;
    };

    set('kpi-monitorados', state.loading ? '...' : state.data.length.toLocaleString());
    set('kpi-hate', state.loading ? '...' : state.stats.hate.toLocaleString());
    set('kpi-total', state.loading ? '...' : state.stats.total.toLocaleString());

    const res = state.stats.total > 0
        ? (100 - ((state.stats.hate / state.stats.total) * 100)).toFixed(1)
        : '100.0';
    set('kpi-res', state.loading ? '...' : `${res}%`);
}

function renderTopbar() {
    const syncEl = document.getElementById('status-sync');
    const filterEl = document.getElementById('active-filter');

    if (syncEl) {
        syncEl.innerText = state.lastSyncAt
            ? `Sincronizado: ${new Date(state.lastSyncAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
            : 'Aguardando leitura...';
    }

    if (filterEl) {
        if (state.selectedAlvo) {
            filterEl.innerHTML = `
                <div class="filter-pill" style="background: rgba(37, 99, 235, 0.2); padding: 4px 12px; border-radius: 20px; font-size: 11px; display: flex; align-items: center; gap: 8px; border: 1px solid rgba(37, 99, 235, 0.4);">
                    <i data-lucide="crosshair" class="w-3 h-3"></i>
                    Foco: @${state.selectedAlvo.username}
                    <button type="button" onclick="window.setFiltroAlvo(null)" style="background: none; border: 0; color: white; cursor: pointer;">
                        <i data-lucide="x" class="w-3 h-3"></i>
                    </button>
                </div>
            `;
        } else {
            filterEl.innerHTML = '';
        }
    }
}

function renderAlertasFeed() {
    const container = document.getElementById('feed-alertas');
    if (!container) return;

    if (state.loading) {
        container.innerHTML = createEmptyState('loader', 'Atualizando alertas', 'Sincronizando com o banco...');
        return;
    }

    const list = state.selectedAlvo
        ? state.alertas.filter((alerta) => String(alerta.candidato_id) === String(state.selectedAlvo.id) || String(alerta.candidatos?.username) === String(state.selectedAlvo.username))
        : state.alertas;

    if (!list.length) {
        container.innerHTML = createEmptyState('shield-check', 'Nenhum alerta ativo', 'Sem sinais críticos para este filtro.');
        return;
    }

    container.innerHTML = list.map((alerta) => {
        const severity = Number(alerta.confianca || 0.85);
        const agressor = alerta.autor_username || 'anônimo';
        return `
            <article class="alert-card">
                <div class="alert-card__header">
                    <div>
                        <span class="eyebrow" style="color:var(--danger)">Agressor: @${agressor}</span>
                        <h4>➔ contra @${alerta.candidatos?.username || 'alvo'}</h4>
                    </div>
                    <span class="severity-pill">${Math.round(severity * 100)}% precisão</span>
                </div>
                <p>"${alerta.texto_bruto || 'Sem conteúdo'}"</p>
                <div class="alert-card__meta">
                    <span>${formatCategory(alerta.categoria_ia || 'ódio')}</span>
                    <span>${new Date(alerta.data_coleta || Date.now()).toLocaleString('pt-BR')}</span>
                </div>
            </article>
        `;
    }).join('');
}

function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    const insights = document.getElementById('monitor-insights');
    if (!container) return;

    if (state.loading) {
        container.innerHTML = createEmptyState('loader', 'Compilando...', '');
        return;
    }

    const rankingMap = {};
    state.alertas.forEach((alerta) => {
        const id = alerta.candidato_id;
        if (!rankingMap[id]) {
            const candidateInfo = state.data.find((item) => String(item.id) === String(id));
            rankingMap[id] = {
                id,
                username: alerta.candidatos?.username || candidateInfo?.username || 'desconhecido',
                count: 0,
                total_comments: candidateInfo?.comentarios_totais_count || 100 
            };
        }
        rankingMap[id].count += 1;
    });

    const hotList = Object.values(rankingMap).sort((a, b) => b.count - a.count);

    container.innerHTML = hotList.map((alvo, index) => {
        const ratio = ((alvo.count / alvo.total_comments) * 100).toFixed(1);
        const isActive = state.selectedAlvo && (String(state.selectedAlvo.id) === String(alvo.id) || String(state.selectedAlvo.username) === String(alvo.username));
        return `
            <button type="button" onclick="window.setFiltroAlvo('${alvo.id}')" class="monitor-row ${isActive ? 'is-active' : ''}">
                <div class="monitor-row__title">
                    <div>
                        <span class="eyebrow">Prioridade ${index + 1}</span>
                        <strong>@${alvo.username}</strong>
                    </div>
                    <span>${alvo.count} ataques</span>
                </div>
                <div class="progress-track">
                    <div class="progress-bar" style="width:${Math.min(ratio * 5, 100)}%"></div>
                </div>
                <div class="monitor-row__meta">
                    <span>Taxa de Hostilidade</span>
                    <span>${ratio}% da amostragem</span>
                </div>
            </button>
        `;
    }).join('');

    if (insights) {
        const top = hotList[0];
        const coverage = state.stats.total > 0 ? ((state.stats.hate / state.stats.total) * 100).toFixed(2) : '0.00';
        insights.innerHTML = `
            <article class="insight-card">
                <span class="eyebrow">Alvo mais visado</span>
                <strong>@${top?.username || '---'}</strong>
                <p>${top?.count || 0} ataques capturados.</p>
            </article>
            <article class="insight-card">
                <span class="eyebrow">Índice Global</span>
                <strong>${coverage}%</strong>
                <p>Volume de ódio no universo total.</p>
            </article>
        `;
    }
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid-container');
    const resultCount = document.getElementById('dossie-result-count');
    if (!container) return;

    document.querySelectorAll('.group-btn').forEach((btn) => {
        btn.classList.toggle('active', btn.dataset.grouping === state.dossieGrouping);
    });

    if (state.loading) {
        container.innerHTML = createEmptyState('loader', 'Organizando dossies', 'Aplicando agrupamentos...');
        return;
    }

    let data = [...state.data];
    if (state.dossieSearch) {
        data = data.filter((item) => {
            const haystack = [item.username, item.nome_completo, item.estado].join(' ').toLowerCase();
            return haystack.includes(state.dossieSearch);
        });
    }

    if (resultCount) resultCount.innerText = `${data.length} registros visíveis`;

    const groups = {};
    if (state.dossieGrouping === 'agressoes') {
        const withHate = data.filter((item) => (item.comentarios_odio_count || 0) > 0).sort((a, b) => (b.comentarios_odio_count || 0) - (a.comentarios_odio_count || 0));
        const withoutHate = data.filter((item) => (item.comentarios_odio_count || 0) === 0);
        groups['Sinais Críticos de Ódio'] = withHate;
        groups['Zonas de Estabilidade'] = withoutHate;
    } else {
        data.forEach((item) => {
            const key = item.estado || 'Território Nacional';
            if (!groups[key]) groups[key] = [];
            groups[key].push(item);
        });
    }

    container.innerHTML = Object.entries(groups).filter(([_, members]) => members.length > 0).map(([name, members]) => `
        <section class="dossie-group">
            <header class="dossie-group__header" style="border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 12px; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span class="status-chip ${name.includes('Críticos') ? 'is-danger' : 'is-ok'}" style="transform: scale(0.8);">
                        ${name.includes('Críticos') ? 'Risco' : 'Seguro'}
                    </span>
                    <h4>${name}</h4>
                </div>
                <strong style="color: var(--text-muted); font-size: 0.75rem;">${members.length} ALVOS</strong>
            </header>
            <div class="dossie-card-grid">
                ${members.map((item) => {
                    const total = Number(item.comentarios_totais_count || 0);
                    const hate = Number(item.comentarios_odio_count || 0);
                    const ratio = total > 0 ? ((hate / total) * 100).toFixed(1) : '0.0';
                    return `
                        <button type="button" onclick="window.inspectTarget('${item.id}')" class="dossie-card ${hate > 0 ? 'is-risk' : ''}">
                            <div class="dossie-card__header">
                                <span class="eyebrow" style="color: ${hate > 0 ? 'var(--danger)' : 'var(--accent)'}">${item.estado || 'BR'}</span>
                                <i data-lucide="${hate > 0 ? 'zap' : 'shield'}" class="w-3 h-3"></i>
                            </div>
                            <h5> @${item.username}</h5>
                            <p style="font-size: 0.8rem; height: 32px; overflow: hidden; opacity: 0.7;">${item.nome_completo || 'Monitorado Ativo'}</p>
                            <div class="dossie-card__stats" style="background: rgba(0,0,0,0.2); border-radius: 12px; padding: 8px;">
                                <div><span style="font-size: 0.6rem;">Alertas</span><strong style="color: ${hate > 0 ? 'var(--danger)' : 'inherit'}">${hate}</strong></div>
                                <div><span style="font-size: 0.6rem;">Amostra</span><strong>${total}</strong></div>
                                <div><span style="font-size: 0.6rem;">PASA %</span><strong>${ratio}</strong></div>
                            </div>
                        </button>
                    `;
                }).join('')}
            </div>
        </section>
    `).join('');
}

function renderGeopolitica() {
    const container = document.getElementById('map-container');
    if (!container) return;

    if (state.loading) {
        container.innerHTML = createEmptyState('loader', 'Compilando mapa', 'Consolidando dados territoriais...');
        return;
    }

    const ufStats = state.data.reduce((acc, item) => {
        const uf = item.estado || 'BR';
        if (!acc[uf]) acc[uf] = { alvos: 0, odio: 0 };
        acc[uf].alvos += 1;
        acc[uf].odio += Number(item.comentarios_odio_count || 0);
        return acc;
    }, {});

    const sortedUFs = Object.entries(ufStats).sort((a, b) => b[1].odio - a[1].odio).slice(0, 5);
    const selectedState = state.selectedUF ? ufStats[state.selectedUF] : null;

    container.innerHTML = `
        <section class="map-shell glass-card">
            <div class="section-heading">
                <div>
                    <span class="eyebrow">Vigilancia territorial</span>
                    <h3>Mapa federativo</h3>
                </div>
                <span class="section-hint">Clique em um estado para detalhamento.</span>
            </div>
            <div id="svg-map-br" class="map-stage"></div>
        </section>
        <aside class="map-panel glass-card">
            <div class="section-heading">
                <div>
                    <span class="eyebrow">Leitura atual</span>
                    <h3 id="st-name">${state.selectedUF || 'Brasil'}</h3>
                </div>
                ${state.selectedUF ? '<button type="button" class="ghost-btn" onclick="window.clearUFSelection()">Limpar</button>' : ''}
            </div>
            <div class="map-kpis">
                <div><span>Alvos</span><strong id="st-targets">${state.selectedUF ? (selectedState?.alvos || 0) : state.data.length}</strong></div>
                <div><span>Alertas</span><strong id="st-hate">${state.selectedUF ? (selectedState?.odio || 0) : state.stats.hate}</strong></div>
            </div>
            <div class="hotspot-list">
                <span class="eyebrow">Ufs mais tensionadas</span>
                ${sortedUFs.map(([uf, info], index) => `
                    <button type="button" class="hotspot-row ${state.selectedUF === uf ? 'is-active' : ''}" onclick="window.selectUF('${uf}')">
                        <span>#${index + 1} ${uf}</span>
                        <strong>${info.odio}</strong>
                    </button>
                `).join('')}
            </div>
        </aside>
    `;

    renderBrazilMap('svg-map-br', ufStats, (name, data, ufId) => {
        state.selectedUF = ufId;
        renderAll();
    });
}

function createEmptyState(icon, title, description) {
    return `
        <div class="empty-state">
            <div class="empty-state__icon"><i data-lucide="${icon}" class="w-5 h-5"></i></div>
            <strong>${title}</strong>
            <p>${description}</p>
        </div>
    `;
}

function formatCategory(category) {
    return String(category).replace(/_/g, ' ').toUpperCase();
}

window.inspectTarget = (id) => {
    const alvo = state.data.find((item) => String(item.id) === String(id));
    if (alvo) {
        state.selectedAlvo = alvo;
        state.view = 'monitor';
        window.location.hash = 'monitor';
        renderAll();
    }
};

window.setDossieGrouping = setDossieGrouping;
window.setDossieSearch = setDossieSearch;

window.setFiltroAlvo = (id) => {
    state.selectedAlvo = id ? state.data.find((item) => String(item.id) === String(id) || String(item.username) === String(id)) : null;
    renderAll();
};

window.selectUF = (uf) => {
    state.selectedUF = uf;
    window.__selectedUF = uf;
    renderAll();
};

window.clearUFSelection = () => {
    state.selectedUF = null;
    window.__selectedUF = null;
    renderAll();
};
