import { state, setDossieGrouping, setDossieSearch } from './state.js';
import { renderBrazilMap } from '../components/BrazilMap.js';
import { planService } from '../services/dataService.js';

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
    if (!state.summary) return;
    
    const set = (id, value, trend = 0) => {
        const el = document.getElementById(id);
        if (!el) return;
        
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

    set('kpi-monitorados', s.total_monitorados.toLocaleString());
    set('kpi-hate', s.total_alertas.toLocaleString(), t.hate_trend_pct);
    set('kpi-total', formatCompactNumber(s.total_amostra));
    set('kpi-res', `${s.resiliencia}%`, t.resiliencia_trend_pct);
}

function formatCompactNumber(number) {
    if (number < 1000) return number;
    if (number < 1000000) return (number / 1000).toFixed(1) + 'K';
    return (number / 1000000).toFixed(1) + 'M';
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
                    Foco: @${planService.maskName(state.selectedAlvo.username)}
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

    if (!planService.canAccess('alerts')) {
        container.innerHTML = createUpgradeGate('Acesso Pro Necessário', 'O feed de alertas ativos é exclusivo para assinantes.');
        return;
    }

    const list = state.selectedAlvo
        ? state.alertas.filter((alerta) => String(alerta.candidato_id) === String(state.selectedAlvo.username) || String(alerta.candidatos?.username) === String(state.selectedAlvo.username))
        : state.alertas;

    if (!list.length) {
        container.innerHTML = createEmptyState('shield-check', 'Nenhum alerta ativo', 'Sem sinais críticos para este filtro.');
        return;
    }

    container.innerHTML = list.map((alerta) => {
        const severity = alerta.severidade || 'INFO';
        const agressor = alerta.autor_username || 'anônimo';
        const target = planService.maskName(alerta.candidatos?.username || alerta.candidato_id || 'alvo');
        
        return `
            <article class="alert-card border-${severity.toLowerCase()}">
                <div class="alert-card__header">
                    <div>
                        <span class="eyebrow" style="color:var(--danger)">Agressor: @${agressor}</span>
                        <h4>➔ contra @${target}</h4>
                    </div>
                    <span class="severity-pill is-${severity.toLowerCase()}">${severity}</span>
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
    const insights = document.getElementById('monitor-insights');
    if (!container) return;

    if (state.loading) {
        container.innerHTML = createEmptyState('loader', 'Compilando...', '');
        return;
    }

    const hotList = [...state.data].sort((a, b) => (b.score_risco || 0) - (a.score_risco || 0));

    container.innerHTML = hotList.map((alvo, index) => {
        const ratio = alvo.comentarios_totales_count > 0 ? ((alvo.comentarios_odio_count / alvo.comentarios_totales_count) * 100).toFixed(1) : '0.0';
        const isActive = state.selectedAlvo && state.selectedAlvo.username === alvo.username;
        const name = planService.maskName(alvo.username);
        
        return `
            <button type="button" onclick="window.setFiltroAlvo('${alvo.username}')" class="monitor-row ${isActive ? 'is-active' : ''}">
                <div class="monitor-row__title">
                    <div>
                        <span class="eyebrow">Prioridade ${index + 1}</span>
                        <strong>@${name}</strong>
                    </div>
                    <span>${alvo.comentarios_odio_count} ataques</span>
                </div>
                <div class="progress-track">
                    <div class="progress-bar" style="width:${alvo.score_risco}%; background:${alvo.color || 'var(--danger)'}"></div>
                </div>
                <div class="monitor-row__meta">
                    <span>Score de Risco: ${alvo.score_risco}</span>
                    <span>${ratio}% de toxicidade</span>
                </div>
            </button>
        `;
    }).join('');

    if (insights) {
        if (state.pasa && state.pasa.length) {
            const topCat = state.pasa[0];
            insights.innerHTML = `
                <article class="insight-card">
                    <span class="eyebrow">Maior Incidência</span>
                    <strong style="color:${topCat.color}">${topCat.label}</strong>
                    <p>${topCat.total} ocorrências (${topCat.percentual}%).</p>
                </article>
                <article class="insight-card">
                    <span class="eyebrow">Resiliência Global</span>
                    <strong>${state.summary.resiliencia}%</strong>
                    <p>Média de estabilidade dos perfis.</p>
                </article>
            `;
        }
    }
}

function renderNetworkIntelligence() {
    const container = document.getElementById('view-networks');
    if (!container) return;

    if (!planService.canAccess('networks')) {
        container.innerHTML = createUpgradeGate('Inteligência de Redes', 'A detecção de redes coordenadas é exclusiva para o plano Enterprise.');
        return;
    }

    const networks = state.networks || [];
    if (!networks.length) {
        container.innerHTML = createEmptyState('activity', 'Nenhuma rede coordenada', 'O pipeline ainda não identificou padrões de ataques em massa.');
        return;
    }

    container.innerHTML = `
        <div class="section-heading">
            <div>
                <span class="eyebrow">Detecção Algorítmica</span>
                <h3>Redes Coordenadas</h3>
            </div>
        </div>
        <div class="networks-grid">
            ${networks.map(n => `
                <div class="network-card glass-card">
                    <div class="network-card__header">
                        <span class="status-badge is-${n.status.toLowerCase()}">${n.status}</span>
                        <span class="severity-value">${n.severidade}</span>
                    </div>
                    <h4>${n.nome}</h4>
                    <p>${n.descricao}</p>
                    <div class="network-keywords">
                        ${n.palavras_chave.slice(0, 5).map(k => `<span>#${k}</span>`).join('')}
                    </div>
                    <div class="network-stats">
                        <div><span>Alvos</span><strong>${n.alvos_vinculados}</strong></div>
                        <div><span>Eventos</span><strong>${n.eventos_count}</strong></div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function renderDossieGrid() {
    const container = document.getElementById('dossie-grid-container');
    const resultCount = document.getElementById('dossie-result-count');
    if (!container) return;

    if (!planService.canAccess('targets')) {
        container.innerHTML = createUpgradeGate('Relatórios Avançados', 'Os dossiês detalhados com score composto são para usuários Pro.');
        return;
    }

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
    if (state.dossieGrouping === 'score') {
        const critico = data.filter(i => i.nivel_risco === 'CRITICO');
        const elevado = data.filter(i => i.nivel_risco === 'ELEVADO');
        const monitor = data.filter(i => i.nivel_risco === 'MONITORANDO');
        const controlado = data.filter(i => i.nivel_risco === 'CONTROLADO');
        if (critico.length) groups['🔴 Alvos Críticos'] = critico;
        if (elevado.length) groups['🟠 Risco Elevado'] = elevado;
        if (monitor.length) groups['🔵 Sob Monitoramento'] = monitor;
        if (controlado.length) groups['🟢 Situação Controlada'] = controlado;
    } else {
        data.forEach((item) => {
            const key = item.estado || 'Território Nacional';
            if (!groups[key]) groups[key] = [];
            groups[key].push(item);
        });
    }

    container.innerHTML = Object.entries(groups).filter(([_, members]) => members.length > 0).map(([name, members]) => `
        <section class="dossie-group">
            <header class="dossie-group__header">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <h4>${name}</h4>
                </div>
                <strong style="color: var(--text-muted); font-size: 0.75rem;">${members.length} ALVOS</strong>
            </header>
            <div class="dossie-card-grid">
                ${members.map((item) => `
                    <button type="button" onclick="window.inspectTarget('${item.username}')" class="dossie-card border-${item.nivel_risco?.toLowerCase()}">
                        <div class="dossie-card__header">
                            <span class="eyebrow" style="color: ${item.color}">${item.estado || 'BR'}</span>
                            <span class="score-badge" style="background:${item.color}">${item.score_risco}</span>
                        </div>
                        <h5> @${item.username}</h5>
                        <p style="font-size: 0.8rem; height: 32px; overflow: hidden; opacity: 0.7;">${item.nome_completo || 'Monitorado Ativo'}</p>
                        <div class="dossie-card__stats">
                            <div><span style="font-size: 0.6rem;">Alertas</span><strong>${item.comentarios_odio_count}</strong></div>
                            <div><span style="font-size: 0.6rem;">Amostra</span><strong>${item.comentarios_totales_count}</strong></div>
                            <div><span style="font-size: 0.6rem;">Risco</span><strong>${item.nivel_risco}</strong></div>
                        </div>
                    </button>
                `).join('')}
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

    const geoData = state.geo || [];
    const ufStats = geoData.reduce((acc, item) => {
        acc[item.uf] = { alvos: item.total_alvos, odio: item.total_hate, color: item.color };
        return acc;
    }, {});

    const sortedUFs = [...geoData].sort((a, b) => b.total_hate - a.total_hate).slice(0, 5);
    const selectedState = state.selectedUF ? geoData.find(i => i.uf === state.selectedUF) : null;

    container.innerHTML = `
        <section class="map-shell glass-card">
            <div class="section-heading">
                <div>
                    <span class="eyebrow">Vigilancia territorial</span>
                    <h3>Mapa geopolítico</h3>
                </div>
            </div>
            <div id="svg-map-br" class="map-stage"></div>
        </section>
        <aside class="map-panel glass-card">
            <div class="section-heading">
                <div>
                    <span class="eyebrow">Análise Regional</span>
                    <h3 id="st-name">${state.selectedUF || 'Brasil'}</h3>
                </div>
            </div>
            <div class="map-kpis">
                <div><span>Alvos</span><strong>${selectedState ? selectedState.total_alvos : state.summary.total_monitorados}</strong></div>
                <div><span>Alertas</span><strong>${selectedState ? selectedState.total_hate : state.summary.total_alertas}</strong></div>
            </div>
            <div class="hotspot-list">
                <span class="eyebrow">Ufs mais tensionadas</span>
                ${sortedUFs.map(([uf, info], index) => `
                    <button type="button" class="hotspot-row ${state.selectedUF === uf ? 'is-active' : ''}" onclick="window.selectUF('${uf}')">
                        <span>#${index + 1} ${uf}</span>
                        <strong>${info.total_hate}</strong>
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

function createUpgradeGate(title, description) {
    return `
        <div class="upgrade-gate glass-card">
            <div class="upgrade-gate__icon"><i data-lucide="lock" class="w-8 h-8"></i></div>
            <h3>${title}</h3>
            <p>${description}</p>
            <button class="cta-upgrade" onclick="window.open('/pricing')">Fazer Upgrade →</button>
        </div>
    `;
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

window.inspectTarget = (username) => {
    const alvo = state.data.find((item) => item.username === username);
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
    state.selectedAlvo = id ? state.data.find((item) => item.username === id) : null;
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
