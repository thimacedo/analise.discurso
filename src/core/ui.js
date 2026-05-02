import { state, setViewState, setNetworkView } from './state.js';
import { dataService } from '../services/dataService.js';

export function renderAll() {
    try {
        updateSidebarActive();
        renderKPIs();
        renderSTN();

        const views = ['monitor', 'networks', 'dossie', 'map', 'directory'];
        views.forEach((view) => {
            const el = document.getElementById(`view-${view}`);
            if (el) el.classList.toggle('active-view', state.view === view);
        });

        if (state.view === 'monitor') {
            renderAlertasFeed(state.alertas);
            renderMonitorImpacto();
        }

        if (window.lucide) lucide.createIcons();
    } catch (e) {
        console.error('Render error:', e);
    }
}

// --- ROLAGEM INFINITA ---
export function initInfiniteScroll() {
    const sentinel = document.getElementById('scroll-sentinel');
    if (!sentinel) return;

    const observer = new IntersectionObserver(async (entries) => {
        if (entries[0].isIntersecting && !state.isLoading && state.view === 'monitor') {
            state.isLoading = true;
            const spinner = document.getElementById('loading-spinner');
            if (spinner) spinner.style.display = 'flex';
            
            try {
                const nextPage = state.currentPage + 1;
                const newAlertas = await dataService.fetchMoreAlertas(nextPage);
                
                if (newAlertas && newAlertas.length > 0) {
                    state.currentPage = nextPage;
                    state.alertas = [...state.alertas, ...newAlertas];
                    appendAlertasFeed(newAlertas);
                }
            } catch (e) {
                console.error('[InfiniteScroll] Error:', e);
            } finally {
                state.isLoading = false;
                if (spinner) spinner.style.display = 'none';
                if (window.lucide) lucide.createIcons();
            }
        }
    }, { rootMargin: '400px' });

    observer.observe(sentinel);
}

export function renderAlertasFeed(list) {
    const container = document.getElementById('feed-alertas');
    if (!container) return;
    container.innerHTML = list.map(alerta => buildPostCard(alerta)).join('');
}

function appendAlertasFeed(newList) {
    const container = document.getElementById('feed-alertas');
    if (!container) return;
    container.insertAdjacentHTML('beforeend', newList.map(alerta => buildPostCard(alerta)).join(''));
}

function buildPostCard(alerta) {
    const target = alerta.candidato_id || 'alvo';
    const agressor = alerta.autor_username || 'anônimo';
    const initials = String(agressor).substring(0, 2).toUpperCase();
    const dateStr = new Date(alerta.data_coleta).toLocaleTimeString('pt-BR');
    const severity = alerta.severidade || 'INFO';
    
    return `
        <article class="post-card animate-in">
            <div class="post-header">
                <div class="post-avatar">${initials}</div>
                <div class="post-user-info">
                    <div class="post-username">@${agressor.replace('@','')}</div>
                    <div class="post-meta">➔ @${target} • ${dateStr}</div>
                </div>
                <div class="severity-pill is-${severity.toLowerCase()}">${severity}</div>
            </div>
            <div class="post-content">
                ${alerta.texto_bruto || 'Sem conteúdo'}
            </div>
            <div class="post-actions">
                <button class="action-btn"><i data-lucide="shield-alert" class="w-4 h-4"></i> Analisar</button>
                <button class="action-btn"><i data-lucide="message-square" class="w-4 h-4"></i> Contexto</button>
                <button class="action-btn" onclick="window.markFalsePositive('${alerta.id}')"><i data-lucide="thumbs-down" class="w-4 h-4"></i> Falso</button>
            </div>
        </article>
    `;
}

function renderMonitorImpacto() {
    const container = document.getElementById('chartMain');
    if (!container) return;
    
    container.innerHTML = state.data.map((alvo, index) => {
        const isActive = state.selectedAlvo && state.selectedAlvo.username === alvo.username;
        return `
            <div onclick="window.setFiltroAlvo('${alvo.username}')" class="monitor-row ${isActive ? 'is-active' : ''}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <strong>@${alvo.username}</strong>
                    <span style="font-size:0.7rem; color:var(--danger); font-weight:800;">${alvo.comentarios_odio_count}!</span>
                </div>
                <div style="font-size:0.7rem; color:var(--text-soft); margin-top:4px;">Risco: ${alvo.score_risco}% • Prio ${index+1}</div>
            </div>
        `;
    }).join('');
}

function renderKPIs() {
    if (!state.summary) return;
    const s = state.summary;
    const update = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.innerText = val;
    };
    update('kpi-monitorados', s.total_monitorados);
    update('kpi-hate', s.total_alertas);
    update('kpi-total', s.total_amostra.toLocaleString());
    update('kpi-res', s.resiliencia + '%');
}

function renderSTN() {
    const el = document.getElementById('stn-balance');
    if (el) el.innerText = `${state.stn_tokens} STN`;
}

function updateSidebarActive() {
    document.querySelectorAll('.nav-item').forEach(nav => {
        const href = nav.getAttribute('href').substring(1);
        nav.classList.toggle('active', state.view === href);
    });
}

// Global exposure
window.setFiltroAlvo = (id) => {
    state.selectedAlvo = id ? state.data.find(item => item.username === id) : null;
    renderAll();
};

window.setViewState = setViewState;
window.setNetworkView = setNetworkView;
