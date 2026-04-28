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
    const titleEl = document.getElementById('status-title');
    const subtitleEl = document.getElementById('status-subtitle');
    const chipEl = document.getElementById('status-chip');
    const syncEl = document.getElementById('status-sync');
    const filterEl = document.getElementById('active-filter');

    if (titleEl) {
        titleEl.innerText = state.selectedAlvo
            ? `Foco atual: @${state.selectedAlvo.username}`
            : 'Panorama operacional do monitoramento';
    }

    if (subtitleEl) {
        if (state.error) {
            subtitleEl.innerText = state.error;
        } else if (state.loading) {
            subtitleEl.innerText = 'Atualizando sinais, alertas e agrupamentos.';
        } else {
            subtitleEl.innerText = `${state.alertas.length} alertas recentes prontos para triagem.`;
        }
    }

    if (chipEl) {
        chipEl.className = `status-chip ${state.error ? 'is-danger' : state.loading ? 'is-warn' : 'is-ok'}`;
        chipEl.innerText = state.error ? 'Dados instaveis' : state.loading ? 'Sincronizando' : 'Sinal operacional';
    }

    if (syncEl) {
        syncEl.innerText = state.lastSyncAt
            ? `Ultima leitura: ${new Date(state.lastSyncAt).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`
            : 'Aguardando primeira leitura';
    }

    if (filterEl) {
        if (state.selectedAlvo) {
            filterEl.innerHTML = `
                <span class="filter-pill">
                    <i data-lucide="crosshair" class="w-3 h-3"></i>
                    @${state.selectedAlvo.username}
                    <button type="button" onclick="window.setFiltroAlvo(null)" aria-label="Limpar foco">
                        <i data-lucide="x" class="w-3 h-3"></i>
                    </button>
                </span>
            `;
        } else {
            filterEl.innerHTML = '<span class="filter-hint">Sem alvo travado. A selecao no ranking refina o feed.</span>';
        }
    }
}

function renderAlertasFeed() {
    const container = document.getElementById('feed-alertas');
    if (!container) return;

    if (state.loading) {
        container.innerHTML = createEmptyState('loader', 'Atualizando alertas', 'Os eventos mais recentes vao aparecer aqui assim que a sincronizacao terminar.');
        return;
    }

    const list = state.selectedAlvo
        ? state.alertas.filter((alerta) => String(alerta.candidato_id) === String(state.selectedAlvo.id))
        : state.alertas;

    if (!list.length) {
        container.innerHTML = createEmptyState('shield-check', 'Nenhum alerta ativo', 'Nao ha sinais criticos para o filtro atual.');
        return;
    }

    container.innerHTML = list.map((alerta) => {
        const severity = Number(alerta.confianca || alerta.confianca_ia || 0.85);
        const createdAt = alerta.data_coleta || alerta.criado_em;
        return `
            <article class="alert-card">
                <div class="alert-card__header">
                    <div>
                        <span class="eyebrow">Ataque detectado</span>
                        <h4>@${alerta.candidatos?.username || 'monitorado'}</h4>
                    </div>
                    <span class="severity-pill">${Math.round(severity * 100)}% confianca</span>
                </div>
                <p>${alerta.texto_bruto || alerta.texto || 'Sem texto disponivel.'}</p>
                <div class="alert-card__meta">
                    <span>${formatCategory(alerta.categoria_ia || 'odio')}</span>
                    <span>${createdAt ? new Date(createdAt).toLocaleString('pt-BR') : 'Agora'}</span>
                </div>
            </article>
        `;
    }).join('');
}

function renderNetworkIntelligence() {
    const container = document.getElementById('network-analysis-grid');
    const summary = document.getElementById('network-summary');
    if (!container) return;

    if (state.loading) {
        container.innerHTML = createEmptyState('loader', 'Calculando rede', 'Agrupando autores e reincidencias para medir coordenacao.');
        if (summary) summary.innerText = 'Carregando perfis e conexoes.';
        return;
    }

    const networkMap = {};
    state.alertas.forEach((alerta) => {
        const user = alerta.autor_username || 'anonimo';
        if (!networkMap[user]) networkMap[user] = { volume: 0, hate: 0, targets: new Set() };
        networkMap[user].volume += 1;
        if (alerta.is_hate) networkMap[user].hate += 1;
        networkMap[user].targets.add(alerta.candidato_id);
    });

    const suspectList = Object.entries(networkMap)
        .map(([username, data]) => ({
            username,
            volume: data.volume,
            hate: data.hate,
            targets: data.targets.size,
            risk: Math.round((data.hate / data.volume) * 100)
        }))
        .sort((a, b) => b.hate - a.hate);

    if (summary) {
        summary.innerText = suspectList.length
            ? `${suspectList.length} perfis com recorrencia suficiente para analise comparativa.`
            : 'Sem volume minimo para inferir coordenacao.';
    }

    if (!suspectList.length) {
        container.innerHTML = createEmptyState('share-2', 'Rede ainda silenciosa', 'A inteligencia de redes precisa de reincidencia para destacar suspeitos.');
        return;
    }

    container.innerHTML = suspectList.map((suspeito) => `
        <article class="network-card ${suspeito.risk > 50 ? 'is-critical' : ''}">
            <div class="network-card__header">
                <div class="network-avatar">
                    <i data-lucide="bot" class="w-4 h-4"></i>
                </div>
                <div>
                    <h4>@${suspeito.username}</h4>
                    <span>${suspeito.targets} alvos impactados</span>
                </div>
                <strong>${suspeito.risk}%</strong>
            </div>
            <div class="network-stats">
                <div><span>Volume</span><strong>${suspeito.volume}</strong></div>
                <div><span>Ataques</span><strong>${suspeito.hate}</strong></div>
                <div><span>Risco</span><strong>${suspeito.risk > 50 ? 'Alto' : 'Moderado'}</strong></div>
            </div>
        </article>
    `).join('');
}

function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    const insights = document.getElementById('monitor-insights');
    if (!container) return;

    if (state.loading) {
        container.innerHTML = createEmptyState('loader', 'Compilando alvos', 'Montando o ranking proporcional de hostilidade por monitorado.');
        if (insights) insights.innerHTML = '';
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
                total: candidateInfo?.comentarios_totais_count || 1
            };
        }
        rankingMap[id].count += 1;
    });

    const hotList = Object.values(rankingMap).sort((a, b) => b.count - a.count);

    if (!hotList.length) {
        container.innerHTML = createEmptyState('bar-chart-3', 'Sem ranking calculado', 'Ainda nao ha alertas suficientes para priorizacao por alvo.');
        if (insights) insights.innerHTML = '';
        return;
    }

    container.innerHTML = hotList.map((alvo, index) => {
        const perc = Math.min((alvo.count / (alvo.total || 1)) * 100, 100);
        const isActive = state.selectedAlvo && String(state.selectedAlvo.id) === String(alvo.id);
        return `
            <button type="button" onclick="window.setFiltroAlvo('${alvo.id}')" class="monitor-row ${isActive ? 'is-active' : ''}">
                <div class="monitor-row__title">
                    <div>
                        <span class="eyebrow">Prioridade ${index + 1}</span>
                        <strong>@${alvo.username}</strong>
                    </div>
                    <span>${alvo.count} alertas</span>
                </div>
                <div class="progress-track">
                    <div class="progress-bar" style="width:${perc.toFixed(1)}%"></div>
                </div>
                <div class="monitor-row__meta">
                    <span>Pressao proporcional</span>
                    <span>${perc.toFixed(1)}%</span>
                </div>
            </button>
        `;
    }).join('');

    if (insights) {
        const top = hotList[0];
        const coverage = state.stats.total > 0
            ? ((state.stats.hate / state.stats.total) * 100).toFixed(2)
            : '0.00';
        insights.innerHTML = `
            <article class="insight-card">
                <span class="eyebrow">Maior pressao</span>
                <strong>@${top.username}</strong>
                <p>${top.count} ocorrencias recentes capturadas no feed.</p>
            </article>
            <article class="insight-card">
                <span class="eyebrow">Cobertura hostil</span>
                <strong>${coverage}%</strong>
                <p>Participacao de alertas sobre o universo coletado.</p>
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
        container.innerHTML = createEmptyState('loader', 'Organizando dossies', 'Aplicando agrupamentos, filtros e score de hostilidade.');
        if (resultCount) resultCount.innerText = 'Carregando';
        return;
    }

    let data = [...state.data];
    if (state.dossieSearch) {
        data = data.filter((item) => {
            const haystack = [
                item.username,
                item.nome_completo,
                item.estado,
                item.partido,
                item.ideologia,
                item.sexo
            ].join(' ').toLowerCase();
            return haystack.includes(state.dossieSearch);
        });
    }

    if (resultCount) {
        resultCount.innerText = `${data.length} registros visiveis`;
    }

    if (!data.length) {
        container.innerHTML = createEmptyState('search-x', 'Nenhum alvo encontrado', 'A busca ou o agrupamento atual nao retornou resultados.');
        return;
    }

    const groups = {};
    if (state.dossieGrouping === 'agressoes') {
        const withHate = data.filter((item) => (item.comentarios_odio_count || 0) > 0)
            .sort((a, b) => (b.comentarios_odio_count || 0) - (a.comentarios_odio_count || 0));
        const withoutHate = data.filter((item) => (item.comentarios_odio_count || 0) === 0);
        groups['Sob ataque ativo'] = withHate;
        groups['Ambiente estavel'] = withoutHate;
    } else {
        data.forEach((item) => {
            const key = item[state.dossieGrouping] || 'Nao informado';
            if (!groups[key]) groups[key] = [];
            groups[key].push(item);
        });
    }

    container.innerHTML = Object.entries(groups).map(([name, members]) => `
        <section class="dossie-group">
            <header class="dossie-group__header">
                <div>
                    <span class="eyebrow">Agrupamento atual</span>
                    <h4>${name}</h4>
                </div>
                <strong>${members.length}</strong>
            </header>
            <div class="dossie-card-grid">
                ${members.map((item) => {
                    const total = Number(item.comentarios_totais_count || 0);
                    const hate = Number(item.comentarios_odio_count || 0);
                    const ratio = total > 0 ? ((hate / total) * 100).toFixed(1) : '0.0';
                    return `
                        <button type="button" onclick="window.inspectTarget('${item.id}')" class="dossie-card ${hate > 0 ? 'is-risk' : ''}">
                            <div class="dossie-card__header">
                                <div class="network-avatar">
                                    <i data-lucide="${hate > 0 ? 'shield-alert' : 'shield'}" class="w-4 h-4"></i>
                                </div>
                                <span>${item.estado || 'BR'}</span>
                            </div>
                            <h5>@${item.username}</h5>
                            <p>${item.nome_completo || item.cargo || 'Monitorado sem nome expandido'}</p>
                            <div class="dossie-card__stats">
                                <div><span>Alertas</span><strong>${hate}</strong></div>
                                <div><span>Amostra</span><strong>${total}</strong></div>
                                <div><span>Indice</span><strong>${ratio}%</strong></div>
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
        container.innerHTML = createEmptyState('loader', 'Compilando mapa', 'Consolidando alvos e alertas por unidade federativa.');
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
                <span class="section-hint">Clique em um estado para atualizar o painel lateral.</span>
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
                <div><span>Alvos</span><strong id="st-targets">${selectedState?.alvos ?? state.data.length}</strong></div>
                <div><span>Alertas</span><strong id="st-hate">${selectedState?.odio ?? state.stats.hate}</strong></div>
            </div>
            <div class="hotspot-list">
                <span class="eyebrow">Ufs mais tensionadas</span>
                ${sortedUFs.length ? sortedUFs.map(([uf, info], index) => `
                    <button type="button" class="hotspot-row ${state.selectedUF === uf ? 'is-active' : ''}" onclick="window.selectUF('${uf}')">
                        <span>#${index + 1} ${uf}</span>
                        <strong>${info.odio}</strong>
                    </button>
                `).join('') : '<p class="muted-copy">Sem alertas territoriais suficientes.</p>'}
            </div>
        </aside>
    `;

    renderBrazilMap('svg-map-br', ufStats, (name, data, ufId) => {
        state.selectedUF = ufId;
        const nameEl = document.getElementById('st-name');
        const targetsEl = document.getElementById('st-targets');
        const hateEl = document.getElementById('st-hate');
        if (nameEl) nameEl.innerText = name;
        if (targetsEl) targetsEl.innerText = data.alvos || 0;
        if (hateEl) hateEl.innerText = (data.odio || 0).toLocaleString();
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
        setViewState('monitor');
    }
};

window.setDossieGrouping = setDossieGrouping;
window.setDossieSearch = setDossieSearch;
window.setFiltroAlvo = (id) => {
    state.selectedAlvo = id ? state.data.find((item) => String(item.id) === String(id)) : null;
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
